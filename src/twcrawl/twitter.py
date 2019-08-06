from contextlib import contextmanager
from datetime import datetime, timedelta
from email.utils import parsedate_tz
from typing import Dict, List
from twitter import Twitter, OAuth, TwitterHTTPError
from .models import User, Session


class RateLimitError(Exception):
    """Triggered whenever Twitter responds with `rate limit exceeded` message."""
    pass


@contextmanager
def twitter_scope(client):
    """Provide a scope which automatically handle rate limit exceptions."""
    try:
        yield client
    except TwitterHTTPError as err:
        if err.e.code == 429:
            raise RateLimitError
        else:
            raise err



class TwitterClient:
    def __init__(self, config: Dict[str, str]):
        self.client = Twitter(auth=OAuth(
            config['access_token'],
            config['access_token_secret'],
            config['consumer_key'],
            config['consumer_secret']
        ))

    def user(self, screen_name: str, session: Session) -> User:
        """Fetches the Twitter profile of the given users screen name."""
        with twitter_scope(self.client) as twitter:
            user_obj = twitter.users.show(screen_name=screen_name)
            return self.__to_user(user_obj, session)

    def users(self, ids: List[int], session: Session) -> List[User]:
        """Fetches the Twitter profile of the given list of users IDs."""
        with twitter_scope(self.client) as twitter:
            ids_string = ",".join(str(id) for id in ids)
            query = twitter.users.lookup(user_id=ids_string)
            return list(map(lambda obj: self.__to_user(obj, session), query))

    def friends_ids(self, screen_name: str) -> List[int]:
        """Fetches the IDs of the givens screen names friends on Twitter."""
        with twitter_scope(self.client) as twitter:
            query = twitter.friends.ids(screen_name=screen_name)
            return query["ids"]

    def __to_user(self, obj, session: Session) -> User:
        """Converts the Twitters JSON object to a User models."""
        user = session.query(User).filter(User.id == obj["id"]).one_or_none()
        if user is None:
            user = User(id=obj["id"])
            session.add(user)
        user.name = obj["name"]
        user.screen_name = obj["screen_name"]
        user.description = obj["description"]
        user.location = obj["location"]
        user.url = obj["url"]
        user.protected = obj["protected"]
        user.verified = obj["verified"]
        user.friends_count = obj["friends_count"]
        user.followers_count = obj["followers_count"]
        user.listed_count = obj["listed_count"]
        user.statuses_count = obj["statuses_count"]
        user.favourites_count = obj["favourites_count"]
        user.created_at = self.__to_datetime(obj["created_at"])
        user.profile_crawled_at = datetime.now()
        return user

    def __to_datetime(self, val: str) -> datetime:
        time_tuple = parsedate_tz(val.strip())
        dt = datetime(*time_tuple[:6])
        return dt - timedelta(seconds=time_tuple[-1])
