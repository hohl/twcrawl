# twcrawl - Twitter Network Crawler

Starts at any given Twitter account (for example `realDonaldTrump` or 
`elonmusk`) and follows their relationships to download the profiles of all 
Twitter users into a local database for later batch processing (like 
analyzing the social sentiment).

**Note:** This crawler has been designed to prioritize crawling of accounts with
lots of followers. Depending on your use case you might need to first tweak 
the parameters a bit.

## Setup and Usage

Copy the `config.example.json` into a `config.json` and fill in your Twitter
API credentials. Then run `src/main.py -i realDonaldTrump` (you can replace
`realDonaldTrump` by any Twitter screen name to use as entry point).

This will launch an endless running process, which crawls as many users as
possible (and as fast as allowed by the Twitter API limits). You can pause the 
process by simply killing it and continue the crawling process by starting it 
again by executing `src/main.py` again (no more need for the `-i` parameter).
