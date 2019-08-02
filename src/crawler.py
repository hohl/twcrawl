#!/usr/bin/env python

import argparse
from twcrawl.app import session_scope
from twcrawl.models import init_models, User


def crawl(args):
    with session_scope() as session:
        user = User(id=123456)
        session.add(user)
        session.commit()


parser = argparse.ArgumentParser(
    description="Crawls most influential users on Twitter and downloads their statuses."
)
parser.add_argument(
    "-i",
    "--init",
    action="store_true",
    help="create empty SQLite3 db before start crawling"
)

if __name__ == '__main__':
    args = parser.parse_args()
    if args.init:
        init_models()
    crawl(args)
