from contextlib import contextmanager
from sqlalchemy import Boolean, BigInteger, create_engine, Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///data/twitter.sqlite3')
Session = sessionmaker(bind=engine)

user_relationship = Table(
    'user_relationship', Base.metadata,
    Column('followee_user_id', Integer, ForeignKey("user.id"), primary_key=True),
    Column('follower_user_id', Integer, ForeignKey("user.id"), primary_key=True)
)


class User(Base):
    """ORM entity to store Twitter users."""
    __tablename__ = "user"
    id = Column(BigInteger, primary_key=True)
    name = Column(String(250))
    screen_name = Column(String(250))
    description = Column(Text)
    location = Column(Text)
    url = Column(Text)
    protected = Column(Boolean)
    verified = Column(Boolean)
    friends_count = Column(Integer)
    followers_count = Column(Integer)
    listed_count = Column(Integer)
    statuses_count = Column(Integer)
    favourites_count = Column(Integer)
    created_at = Column(DateTime)
    friends = relationship(
        "User",
        secondary=user_relationship,
        primaryjoin=id == user_relationship.c.followee_user_id,
        secondaryjoin=id == user_relationship.c.follower_user_id,
        backref="followers"
    )
    statuses = relationship(
        "Status",
        backref="user"
    )


class Status(Base):
    """ORM entity to store any Tweet posted by a user in our database."""
    __tablename__ = "status"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('user.id'))
    text = Column(Text)
    in_reply_to_status_id = Column(BigInteger, ForeignKey("status.id"))
    quote_count = Column(Integer)
    reply_count = Column(Integer)
    retweet_count = Column(Integer)
    favorite_count = Column(Integer)
    created_at = Column(DateTime)


def init_models():
    """Creates the required database file and tables."""
    Base.metadata.create_all(engine)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
