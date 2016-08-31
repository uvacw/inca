import requests
import feedparser
from core.scraper_class import Scraper
from core.database import check_exists
import logging
import datetime

logger = logging.getLogger(__name__)

# drawn from https://validator.w3.org/feed/docs/rss2.html
RSS_SPECIFIED_FIELDS = [
    'title',
    'link',
    'description',
    'language',
    'copyright',
    'managingEditor',
    'webMaster',
    'pubDate',
    'lastBuildDate',
    'category',
    'generator',
    'docs',
    'cloud',
    'ttl',
    'image',
    'textInput',
    'skipHours',
    'skipDays'
]


class generic_rss(Scraper):

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
                page = requests.get(link['href'])
                content = page.content
                link.update({'content':content})
                newlinks.append(link)
        return newlinks

    def feedparser_to_dict(self, nested_dict):
        '''Transform feedparser dict to normal dict representation'''
        if type(nested_dict) == bytes: return str(nested_dict)
        if type(nested_dict) == list: return [self.feedparser_to_dict(thing) for thing in nested_dict]
        if not type(nested_dict)==feedparser.FeedParserDict: return nested_dict
        return {k: self.feedparser_to_dict(v) for k,v in nested_dict.items()}

KNOWN_REWRITES = {}