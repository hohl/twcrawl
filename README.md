# twcrawl - Twitter Network Crawler

Starts at any given Twitter user (for example `realDonaldTrump`) and follows
their relationships to download all Twitter users with a lot of followers and
downloads their Tweets.

## Setup and Usage

Copy the `config.example.json` into a `config.json` and fill in your Twitter
API credentials. Then run `src/main.py -i realDonaldTrump` (you can replace
`realDonaldTrump` by any Twitter screen name to use as entry point).

This will launch an endless running process crawl as many users as fast as
possible (as allowed by the Twitter API limits). You can pause the process by
simply killing it and continue the crawling process by starting it again by
executing `src/main.py` (no more need for the `-i` parameter).
