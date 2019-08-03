#!/usr/bin/env python

import asyncio
import argparse
from twcrawl.crawler import crawl
from twcrawl.models import init_models

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
    loop = asyncio.get_event_loop()
    loop.run_until_complete(crawl(args))
    loop.close()
