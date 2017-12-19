#!/usr/bin/env python3
from inca import Inca

myinca  = Inca()

outlets = [outlet for outlet in dir(myinca.rssscrapers) if not outlet.startswith('__')]


for outlet in outlets:
    print("Scraping {}...".format(outlet))
    try:
        eval("myinca.rssscrapers.{}()".format(outlet))
    except Exception as ex:
        print("'\nERROR SCRAPING {}.".format(outlet))
        print(ex)
        print('\n')
