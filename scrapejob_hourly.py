#!/usr/bin/env python3
from inca import Inca

myinca  = Inca()
'''
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
'''


outlets = [e for e in dir(myinca.rssscrapers) if not e.startswith('__')]


for s in outlets:
    print("Scraping {}...".format(s))
    try:
        c = "myinca.rssscrapers.{}()".format(s)
        eval(c)
    except Exception as ex:
        print("'\nERROR SCRAPING {}.".format(s))
        print(ex)
        print('\n')
