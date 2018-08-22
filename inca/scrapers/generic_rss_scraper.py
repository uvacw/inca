import requests
import feedparser
from ..core.scraper_class import Scraper
from ..core.database import check_exists
import logging
import datetime

logger = logging.getLogger("INCA")


class generic_rss(Scraper):
    """Scrapes provided RSS url"""
    def __init__(self):
        self.doctype = "raw RSS "
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=8, day=28)

    def get(self, url):
        '''RSS feed item'''
        feed = requests.get(url)
        parsed = feedparser.parse(feed.content)
        for item in parsed['entries']:
            if check_exists(item.get('id',item.get('link','True')))[0]: continue
            item['feed'] = dict(parsed['feed'])
            item['links'] = self.follow_links(item['links'])
            item['_id'] = item.pop('id')
            yield self.feedparser_to_dict(item)

    def follow_links(self,links):
        newlinks = []
        for link in links:
            if 'text' in link['type']:
                content = self.retrieve_content(link['href'])
                newlinks.append(link)
                link.update({'content': content})
        return newlinks

    def feedparser_to_dict(self, nested_dict):
        '''Transform feedparser dict to normal dict representation'''
        if type(nested_dict) == bytes: return str(nested_dict)
        if type(nested_dict) == list: return [self.feedparser_to_dict(thing) for thing in nested_dict]
        if not type(nested_dict)==feedparser.FeedParserDict: return nested_dict
        return {k: self.feedparser_to_dict(v) for k,v in nested_dict.items()}

    def retrieve_content(self, url):
        '''overwrite with feed-specific logic to parse link content'''
        page = requests.get(url)
        content = page.content
        return content



KNOWN_REWRITES = {}
