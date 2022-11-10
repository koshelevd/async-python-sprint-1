import logging
import multiprocessing as mp
import sys
from multiprocessing.queues import Queue

from tasks import (DataAggregationTask, DataAnalyzingTask, DataFetchingTask)
from utils import CITIES

logging.basicConfig(level=logging.INFO,
                    handlers=(logging.StreamHandler(stream=sys.stdout),))


def forecast_weather() -> None:
    """Forecast weather."""
    ctx = mp.get_context('spawn')
    queue: Queue = Queue(ctx=ctx)
    fetching = DataFetchingTask(CITIES, queue)
    fetching.run()
    aggregating = DataAggregationTask(queue)
    analyzing = DataAnalyzingTask(queue)
    aggregating.run()
    result = analyzing.run()
    logging.info(f'{result=}')


if __name__ == "__main__":
    forecast_weather()
