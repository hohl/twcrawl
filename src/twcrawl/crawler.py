import asyncio
from abc import ABC, abstractmethod
from .models import *


class RateLimitError(Exception):
    """Triggered whenever Twitter responds with `rate limit exceeded` message."""
    pass


class BaseCrawler(ABC):
    """Abstract base class for all crawlers."""
    timeout_seconds = 15. * 60.

    def __init__(self):
        self.__queue = asyncio.Queue()

    def schedule(self, job):
        self.__queue.put_nowait(job)

    async def run(self):
        try:
            job = self.__queue.get_nowait()
            try:
                self.exec(job)
            except RateLimitError:
                await asyncio.sleep(self.timeout_seconds)
                self.__queue.put_nowait(job)
            self.__queue.task_done()
        except asyncio.QueueEmpty:
            self.done()
        finally:
            await asyncio.sleep(0)

    @abstractmethod
    def exec(self, job):
        """Implement to execute the crawlers task."""
        pass

    @abstractmethod
    def done(self):
        """Implement to issue new tasks when all existing tasks are complete."""
        pass


class UsersCrawler(BaseCrawler):
    def exec(self, job):
        print(f"crawl user profile of @{job}...")
        raise RateLimitError()

    def done(self):
        pass


class RelationshipsCrawler(BaseCrawler):
    def exec(self, job):
        print(f"crawl friends of @{job.name}...")
        raise RateLimitError()

    def done(self):
        pass


class StatusesCrawler(BaseCrawler):
    def exec(self, job):
        print(f"crawl statuses for @{job.name}...")
        raise RateLimitError()

    def done(self):
        pass


async def crawl(args):
    async def run_forever(crawler):
        while True:
            await crawler.run()

    user_crawler = UsersCrawler()
    user_crawler.schedule("realDonaldTrump")
    await asyncio.wait(map(run_forever, [
        user_crawler,
        RelationshipsCrawler(),
        StatusesCrawler()
    ]))
