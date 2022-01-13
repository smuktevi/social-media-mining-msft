# config file for scraper
from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class ScraperConfig:
	subreddit_list: List[str] #list of subreddits to scrape
	max_post_count: int #number of hot posts to retrieve
	max_comment_count: int #number of top comments associated with each retrieved post

default_config = scraper_config = ScraperConfig(subreddit_list=['computerscience'],
												max_post_count = 100,
												max_comment_count = 25)
