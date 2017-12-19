#!/usr/bin/env python3
import inca

outlets = ['ad',
       'bd',
       'bndestem',
       'destentor',
       'ed',
       'fok',
       'frieschdagblad',
       'geenstijl',
       'gelderlander',
       'limburger',
       'metronieuws',
       'nos',
       'nrc',
       'nu',
       'parool',
       'pzc',
       'telegraaf',
       'trouw',
       'tubantia',
       'volkskrant',
       'zwartewaterkrant']

for s in outlets:
    print("Scraping {}...".format(s))
    try:
        c = "inca.scrapers.news_scraper.{}().run()".format(s)
        eval(c)
    except:
        print("ERROR SCRAPING {}.".format(s))
