#!/usr/bin/env python3
import inca

outlets = ['parool','geenstijl','telegraaf','trouw','nu','volkskrant','ad','metronieuws','nrc','nos']

for outlet in outlets:
    print("Scraping {}...".format(outlet))
    try:
        c = "inca.scrapers.news_scraper.{}().run()".format(outlet)
        eval(c)
    except:
        print("ERROR SCRAPING {}.".format(outlet))
