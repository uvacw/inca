import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)
'''
from scrapers.corp_abnamro import *
from scrapers.corp_acs import *
from scrapers.corp_aegon import *
from scrapers.corp_akzonobel import *
from scrapers.corp_amadeus import *
from scrapers.corp_asml import *
from scrapers.corp_barclays import *
from scrapers.corp_bat import *
from scrapers.corp_bhp import *
from scrapers.corp_boskalis import *
from scrapers.corp_bp import *
# from scrapers.corp_bsch import *
from scrapers.corp_btgroup import *
from scrapers.corp_compass import *
from scrapers.corp_diageo import *
from scrapers.corp_dsm import *
from scrapers.corp_exxonmobil import *
from scrapers.corp_ferrovial import *
from scrapers.corp_gamesa import *
from scrapers.corp_gemalto import *
from scrapers.corp_glencore import *
from scrapers.corp_gnf import *
from scrapers.corp_gsk import *
from scrapers.corp_iag import *
from scrapers.corp_iberdrola import *
from scrapers.corp_ing import *
from scrapers.corp_kpn import *
from scrapers.corp_lbg import *
from scrapers.corp_mapfre import *
from scrapers.corp_nationalgrid import *
from scrapers.corp_philips import *
from scrapers.corp_prudential import *
from scrapers.corp_randstad import *
from scrapers.corp_ree import *
from scrapers.corp_riotinto import *
from scrapers.corp_sbm import *
from scrapers.corp_shell import *
from scrapers.corp_shire import *
from scrapers.corp_telefonica import *
from scrapers.corp_unilever import *
from scrapers.corp_vodafone import *
from scrapers.corp_vopak import *
from scrapers.corp_walmart import *
from scrapers.corp_wolters import *
'''

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()


if __name__=="__main__":
    print('Please use these scripts from within inca. EXAMPLE: BLA BLA BLA')

