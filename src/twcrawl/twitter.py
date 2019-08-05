from datetime import datetime, timedelta
from email.utils import parsedate_tz
from typing import Dict, List
from twitter import Twitter, OAuth
from .models import User


class RateLimitError(Exception):
    """Triggered whenever Twitter responds with `rate limit exceeded` message."""
    pass


class TwitterClient:
    def __init__(self, config: Dict[str, str]):
        self.twitter = Twitter(auth=OAuth(
            config['access_token'],
            config['access_token_secret'],
            config['consumer_key'],
            config['consumer_secret']
        ))

    def user(self, screen_name: str) -> User:
        """Fetches the Twitter profile of the given users screen name."""
        user_obj = self.twitter.users.show(screen_name=screen_name)
        return self.__to_user(user_obj)

    def friends_ids(self, screen_name: str) -> List[int]:
        """Fetches the IDs of the givens screen names friends on Twitter."""
        query = self.twitter.friends.ids(screen_name=screen_name)
        return query["ids"]

    def __to_user(self, obj) -> User:
        """Converts the Twitters JSON object to a User models."""
        return User(
            id=obj["id"],
            name=obj["name"],
            screen_name=obj["screen_name"],
            description=obj["description"],
            location=obj["location"],
            url=obj["url"],
            protected=obj["protected"],
            verified=obj["verified"],
            friends_count=obj["friends_count"],
            followers_count=obj["followers_count"],
            listed_count=obj["listed_count"],
            statuses_count=obj["statuses_count"],
            favourites_count=obj["favourites_count"],
            created_at=self.__to_datetime(obj["created_at"])
        )

    def __to_datetime(self, val: str) -> datetime:
        time_tuple = parsedate_tz(val.strip())
        dt = datetime(*time_tuple[:6])
        return dt - timedelta(seconds=time_tuple[-1])
