import multiprocessing as mp
from multiprocessing.queues import Queue

from tasks import DataFetchingTask


class TestAPI:
    ctx = mp.get_context('spawn')
    cities = {
        "MOSCOW": "https://code.s3.yandex.net/async-module/moscow-response.json"
    }

    def test_data_fetching_task(self):
        """Test that data fetching task works correctly."""
        queue: Queue = Queue(ctx=self.ctx)
        task = DataFetchingTask(self.cities, queue)
        task.run()
        result = queue.get()
        assert result['geo_object']['locality']['name'] == 'Moscow'
