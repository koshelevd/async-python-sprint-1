import json
import multiprocessing as mp
import os
from multiprocessing.queues import Queue

from fixtures import response, result_fixture
from models.response import YandexResponse
from models.result import Result
from tasks import (
    DataAggregationTask,
    DataAnalyzingTask,
    DataCalculationTask,
    DataFetchingTask,
)


class TestForecasting:
    ctx = mp.get_context('spawn')
    cities = {
        "MOSCOW": "https://code.s3.yandex.net/async-module/moscow-response.json"
    }

    def test_data_fetching_task(self):
        """Test that data fetching task works correctly."""
        queue: Queue = Queue(ctx=self.ctx)
        task = DataFetchingTask(self.cities, queue)
        task.run()
        result: YandexResponse = queue.get()
        assert result.geo_object.locality.name == 'Moscow'

    def test_data_calculation_task(self, response):
        """Test that data calculation task works correctly."""
        task = DataCalculationTask()
        result: Result = task.run(response)
        assert result.city == 'Moscow'
        assert result.avg_temp_all_days == 11.7
        assert result.avg_no_rain_hours == 9.0

    def test_data_aggregation_task(self, response):
        """Test that data aggregation task works correctly."""
        queue: Queue = Queue(ctx=self.ctx)
        queue.put(response)
        queue.put(None)
        task = DataAggregationTask(queue)
        task.run()
        assert os.path.exists('result.json')
        with open('result.json', 'r') as f:
            result_file = json.load(f)
        assert len(result_file) == 1
        result = Result(**result_file[0])
        assert result.city == 'Moscow'
        assert result.avg_temp_all_days == 11.7
        assert result.avg_no_rain_hours == 9.0

    def test_data_analyzing_task(self, result_fixture):
        """Test that data analyzing task works correctly."""
        queue: Queue = Queue(ctx=self.ctx)
        for item in result_fixture + [None]:
            queue.put(item)
        task = DataAnalyzingTask(queue)
        result = task.run()
        assert result == 'Moscow'
