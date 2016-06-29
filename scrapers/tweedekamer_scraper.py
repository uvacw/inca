from core.scraper_class import Scraper
from core.database import check_exists
import logging
import datetime
import requests
from requests import ConnectTimeout
from lxml.html import fromstring

logger = logging.getLogger(__name__)

BASE_URL = 'https://zoek.officielebekendmakingen.nl/h-tk-{fromyear}{toyear}-{number}-{subnumber}.xml'
BASE_METADATA_URL = 'https://zoek.officielebekendmakingen.nl/h-tk-{fromyear}{toyear}-{number}-{subnumber}'

MAX_TRIES = 100 # maximum number of consecutively missing documents 

class tweedekamer_handelingen_scraper(Scraper):
    """Scrapes the Dutch parlementary acts (Handelingen) from the official site as XML blobs with metadata"""
    
    doctype = 'Dutch parlementary acts (Handelingen)'
    version = '.0'
    date    = datetime.datetime(year=2016,month=6,day=7)
    
    def get(self, startyear='1995', back_in_time='False'):
        '''Document collected from 'officielebekendmakingen.nl' as XML files
        by iterating over document numbers in the url'''

        years = range(int(startyear), datetime.datetime.now().year)
        if back_in_time.lower()=="true":
            years = list(years)
            years.reverse()
        tries = 0
        for toyear in years:
            fromyear = toyear-1
            tries = 0
            for number in range(1,10000):
                if tries > MAX_TRIES:
                    logger.info('Finished {toyear} (presumably)'.format(**locals()))
                    break
                subtries = 0
                for subnumber in range(1,1000):
                    logger.info('getting {number}-{subnumber} of {toyear}'.format(**locals()))
                    target =  'h-tk-{fromyear}{toyear}-{number}-{subnumber}'.format(**locals())
                    if check_exists(target)[0]: continue
                    source = BASE_URL.format(**locals())
                    attempt = retrieve(source)
                    if not attempt      : continue
                    if attempt == 'stop':
                        if subtries < 3:
                            subtries += 1
                            continue
                        else:
                            logger.info('finished {number} in {toyear} tries:{tries}'.format(**locals()))
                            tries +=1
                            break
                    tries = 0
                    metadata=retrieve_metadata(BASE_METADATA_URL.format(**locals()))
                    base = {'raw_content': attempt, '_id':target, 'source': source }
                    base.update(metadata)
                    yield base
                    subtries = 0


            

#######
# RETRIEVAL HELPER FUNCTIONS
#######

def retrieve(url, iteration=1):
    try:
        content = requests.get(url)
        if content.status_code == 200 and '404.htm' not in content.url :
            return content.text
        if content.status_code == 404 or '404.htm' in content.url :
            logger.info('No page found: {url}'.format(**locals()))
            return 'stop'
    except Exception as err: 
        if iteration < 3:
            logger.warning('Unable to retrieve, attempting again {url} ({iteration})'.format(**locals()))
            retrieve(url, iteration+1)
        else:
            logger.warning('Unable to retrieve {url}, due to {err} --> skipping'.format(**locals()))
            return False

                    
def parse_document(document):
    parsed_document = dict()
    
    raw = ' '.join(document.split('\n')[1:])
    parsed_document['raw'] = raw

    #xml = XML(raw)
    
    #parsed_document['speakers'] = set(xml.xpath('//spreker//naam//text()'))
    #parsed_document['parties']  = set(xml.xpath('//spreker//partij//text()'))
    #parsed_document['itemname'] = ','.join(xml.xpath('//itemnaam/text()'))
    
    return parsed_document

def retrieve_metadata(url):
    try: 
        metadata_page = requests.get(url, timeout=10)
    except ConnectTimeout:
        return retrieve_metadata(url)
    except:
        logger.warning( 'ack, returning empty') 
        return dict()
    dom = fromstring(metadata_page.text)

    metadata = {row.xpath('./td[1]/text()')[0]:row.xpath('./td[2]//text()')[0] for row in dom.xpath('//tbody/tr')}
    return metadata
