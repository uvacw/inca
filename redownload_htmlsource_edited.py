#!/usr/bin/env python3

import inca
import random
from time import sleep
import datetime
import urllib.error

print(datetime.datetime.now())


print(inca.core.search_utils.list_doctypes())

p = inca.processing.repair_processing.redownload()

# TODO
# fok: need to fix cookie wall first
# geenstijl: need to fix cookie wall first
# ad: need to fix cookie wall first


newspapers = [ { 'doctype': 'ad',
                 'from_time': '2014-04-01',
                 'to_time': '2014-09-01' },
               { 'doctype': 'ad',
                 'from_time': '2016-08-01',
                 'to_time': '2017-04-01' }, 
               #{ 'doctype': 'fok',
               #  'from_time': '2015-02-01',
               #  'to_time': '2017-04-01' },
               # { 'doctype': 'geenstijl',
               #  'from_time': '2014-12-01',
               #  'to_time': '2018-01-01' },
               #{ 'doctype': 'metro',
               #  'from_time': '2014-06-01',
               #  'to_time': '2016-01-01' },
           #{ 'doctype': 'metro',
           #      'from_time': '2017-10-01',
           #    'to_time': '2018-01-01' },
           #     { 'doctype': 'nrc',
           #      'from_time': '2014-05-01',
           #      'to_time': '2017-12-01' },
            #{ 'doctype': 'spits',
            #     'from_time': '2014-01-01',
            #     'to_time': '2015-12-01' },
           #    { 'doctype': 'telegraaf',      AL GEDAAN
           #      'from_time': '2014-01-01',   AL GEDAAN
           #      'to_time': '2018-01-01' },   AL GEDAAN
           #{ 'doctype': 'trouw',
           #      'from_time': '2015-02-01',
           #      'to_time': '2015-06-01' },
           #{ 'doctype': 'trouw',
           #      'from_time': '2016-10-01',
           #      'to_time': '2017-04-01' }
            ]

for newspaper in newspapers:
    print(newspaper['doctype'] + ';' + newspaper['from_time'] + ';' + newspaper['to_time'])
    time_range = { 'range': { 'publication_date': { 'gte': newspaper['from_time'], 'lte': newspaper['to_time'] } } }
    query = { 'query': { 'bool': { 'filter': [{ 'term': { '_type': "{} (www)".format(newspaper['doctype']) }}, time_range] } } }
    print(query)
    ids = [ d['_id'] for d in inca.core.database.scroll_query(query) ]
    if newspaper['doctype'] == 'metro':
        f = eval('inca.rssscrapers.news_scraper.metronieuws.get_page_body')
        g = eval('inca.rssscrapers.news_scraper.metronieuws.getlink')
    else:
       f  = eval('inca.rssscrapers.news_scraper.{}.get_page_body'.format(newspaper['doctype']))
       g  = eval('inca.rssscrapers.news_scraper.{}.getlink'.format(newspaper['doctype']))

    for i in ids:
            print(i)
            sleep(random.uniform(5,10))
            try:
                p.run(i, 'url', downloadfunction=f, linkpreprocessor = g, save=True)
                #print(data['_source']['url_redownload'])
            except urllib.error.HTTPError as e:
                print('HTTPError = ' + str(e.code))
            except urllib.error.URLError as e:
                print('URLError = ' + str(e.reason))
            except Exception as e:
                print('generic exception: ' + str(e))

print(datetime.datetime.now())
