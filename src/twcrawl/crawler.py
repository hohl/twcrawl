import asyncio
import json
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Union, NoReturn
from .models import session_scope
from .twitter import *

T = TypeVar("T")


class BaseCrawler(ABC, Generic[T]):
    """Abstract base class for all crawlers."""
    timeout_seconds = 15 * 60  # Twitter limits are usually "per 15 minutes"

    def __init__(self, client: TwitterClient):
        self.client = client
        self.queue = asyncio.Queue()

    def schedule(self, job: T) -> None:
        self.log(f"Schedule {job}")
        self.queue.put_nowait(job)

    async def run(self) -> None:
        try:
            job = self.queue.get_nowait()
            try:
                self.exec(job)
            except RateLimitError:
                self.log(f"Rate limit reached. Sleep {self.timeout_seconds} seconds…")
                await asyncio.sleep(self.timeout_seconds)
                self.queue.put_nowait(job)
            self.queue.task_done()
        except asyncio.QueueEmpty:
            self.log("Queue empty. Try to find new work...")
            self.done()
            await asyncio.sleep(3)
        except BaseException as error:
            self.log(f"Unexpected exception occurred: {error}")
        finally:
            await asyncio.sleep(0)

    @abstractmethod
    def exec(self, job: T) -> None:
        """Implement to execute the crawlers task."""
        pass

    @abstractmethod
    def done(self) -> None:
        """Implement to issue new tasks when all existing tasks are complete."""
        pass

    def log(self, msg: str) -> None:
        """Helper to log progress."""
        print("[" + self.__class__.__name__ + "] " + msg)  # temporary solution only


class UsersCrawler(BaseCrawler[Union[str, List[int]]]):
    """Crawler to fetch Twitter profiles either by screen name of IDs."""

    def exec(self, job: Union[str, List[int]]) -> None:
        if isinstance(job, str):
            self.__exec_screen_name(job)
        else:
            self.__exec_list_of_ids(job)

    def __exec_screen_name(self, screen_name: str) -> None:
        self.log(f"Crawl user profile of @{screen_name}...")
        with session_scope() as session:
            user = self.client.user(screen_name)
            session.add(user)
            session.commit()

    def __exec_list_of_ids(self, ids: List[int]) -> None:
        assert (len(ids) <= 100)
        self.log(f"Crawl user profiles of @{len(ids)}")
        pass

    def done(self) -> None:
        pass


class RelationsCrawler(BaseCrawler[str]):
    """Crawler to fetch all friends of a given Twitter users screen name.

    (Note: A friend in Twitters definition is somebody you follow.)
    """

    def __init__(self, client: TwitterClient, users_crawler: UsersCrawler):
        super().__init__(client)
        self.users_crawler = users_crawler

    def exec(self, screen_name: str) -> None:
        self.log(f"Crawl friends of @{screen_name}...")
        all_ids = self.client.friends_ids(screen_name)
        self.log(f"Found {len(all_ids)} friends for @{screen_name}.")
        for n in range(0, len(all_ids), 100):
            ids = all_ids[n:n + 100]
            self.users_crawler.schedule(ids)

    def done(self) -> None:
        pass


class StatusesCrawler(BaseCrawler[str]):
    """Crawler to fetch all statuses (=tweets) by a given Twitter users screen name."""

    def exec(self, screen_name: str) -> None:
        raise NotImplementedError

    def done(self) -> None:
        pass


async def __run_forever(crawler: BaseCrawler) -> None:
    """Internal helper to run a crawler forever with asyncio."""
    while True:
        await crawler.run()


async def crawl(args) -> NoReturn:
    """Initiates the crawling process."""
    with open('config.json') as config_file:
        config = json.load(config_file)
        client = TwitterClient(config["twitter"])
    users_crawler = UsersCrawler(client)
    users_crawler.schedule("realDonaldTrump")
    relations_crawler = RelationsCrawler(client, users_crawler)
    statuses_crawler = StatusesCrawler(client)
    await asyncio.wait(map(__run_forever, [
        users_crawler,
        relations_crawler,
        statuses_crawler
    ]))
