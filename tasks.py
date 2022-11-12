import json
import logging
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool, Queue, cpu_count
from typing import Iterator

from api_client import YandexWeatherAPI
from models.response import Hour, YandexResponse
from models.result import Result, Stat


class DataFetchingTask:
    """Class for fetching data from API."""

    api: YandexWeatherAPI = YandexWeatherAPI()

    def __init__(self, cities: dict, queue: Queue):
        self.cities: dict = cities
        self.queue: Queue = queue

    def run(self):
        """Run fetching data from API."""
        logging.info('Fetching data...')
        with ThreadPoolExecutor() as pool:
            fetched_data: Iterator[YandexResponse] = pool.map(
                self.api.get_forecasting,
                self.cities.keys())
            for data in fetched_data:
                city_name = data.geo_object.locality.name
                logging.info(
                    f'City {city_name} fetched')
                self.queue.put(data)
            self.queue.put(None)
        logging.info('Finished fetching data')


class DataCalculationTask:
    """Class for calculating data."""

    no_rain_conditions: tuple = (
        'clear',
        'partly-cloudy',
        'cloudy',
        'overcast',
    )

    def _calc_stats(self, data: list[Hour]) -> tuple[int, int, float]:
        """Calculate stats for one day."""
        hours: int = 0
        no_rain_hours: int = 0
        temp: float = 0.0
        for row in data:
            if 9 <= int(row.hour) <= 19:
                hours += 1
                if row.condition in self.no_rain_conditions:
                    no_rain_hours += 1
                temp += row.temp
        return hours, no_rain_hours, temp

    def run(self, data: YandexResponse) -> Result:
        """Run calculating data."""
        result: Result = Result(city=data.geo_object.locality.name, stats=[],
                                avg_temp_all_days=0.0, avg_no_rain_hours=0.0)
        num_of_days: int = 0
        sum_average_temps: float = 0.0
        sum_no_rain_hours: int = 0
        for forecast in data.forecasts:
            stat = Stat(date=forecast.date, no_rain_hours=0,
                        avg_temp_per_day=0.0)
            hours, no_rain_hours, temp = self._calc_stats(forecast.hours)
            if hours < 11:
                continue
            num_of_days += 1
            stat.no_rain_hours = no_rain_hours
            avg_temp_per_day: float = round(temp / 11, 1)
            sum_average_temps += avg_temp_per_day
            sum_no_rain_hours += no_rain_hours
            stat.avg_temp_per_day = avg_temp_per_day
            result.stats.append(stat)
        result.avg_temp_all_days = round(sum_average_temps / num_of_days, 1)
        result.avg_no_rain_hours = round(sum_no_rain_hours / num_of_days, 1)
        logging.info(f'Finished {result.city} calculation')
        return result


class DataAggregationTask:
    calculator = DataCalculationTask()
    result: list = []

    def __init__(self, queue: Queue):
        self.queue: Queue = queue

    def _cb(self, result: Result) -> None:
        """Callback for multiprocessing."""
        self.result.append(result)
        logging.info(f'Calculated: {result.city}')

    @staticmethod
    def _error_cb(error: BaseException) -> None:
        """Error callback for multiprocessing."""
        logging.exception(f'{error=}')

    def run(self) -> None:
        """Run aggregation data."""
        cores: int = cpu_count()
        logging.info('Data aggregation started')
        with Pool(processes=cores - 1) as pool:
            while data := self.queue.get(block=True, timeout=0):
                result = pool.apply_async(
                    self.calculator.run,
                    (data,),
                    callback=self._cb,
                    error_callback=self._error_cb
                )
                self.queue.put(result.get())
            self.queue.put(None)
        jsonable_result = [item.dict() for item in self.result]
        with open('result.json', 'w+') as f:
            json.dump(jsonable_result, f, indent=2)
        logging.info('Data aggregation finished')


class DataAnalyzingTask:
    """Class for analyzing data."""

    def __init__(self, queue: Queue):
        self.queue: Queue = queue

    def run(self) -> str:
        """Run analyzing data."""
        data: list[Result] = []
        logging.info('Data analyzing started')
        while city_calculated_data := self.queue.get(block=True):
            data.append(city_calculated_data)
        data.sort(key=lambda value: (
            value.avg_no_rain_hours,
            value.avg_temp_all_days
        ),
                  reverse=True)
        logging.info('Data analyzing finished')
        return data[0].city
