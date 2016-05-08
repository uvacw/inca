from core.scraper_class import Scraper
from core.database import document_collection
import logging
import datetime

logger = logging.getLogger(__name__)


class tweede_kamer_scraper(Scraper):

    doctype = 'Dutch parlementary procedures'
    verions = '.0'
    date    = datetime.datetime(year=2016,month=6,day=7)
    
    def get(self):
        '''Document collected from 'officiëlebekendmakingen.nl' as XML files
        by iterating over document numbers in the url'''
        
        years = range(1990, startyear+1)
        tries = 0
        for toyear in years:
            fromyear = toyear-1
            for number in range(1,10000):
                logger.info('getting {number} of {toyear}'.format(**locals()))
                target =  '{fromyear}_{toyear}_{number}.XML'.format(**locals())
                if target in os.listdir(DATA_DIRECTORY): continue
                source = BASE_URL.format(**locals())
                attempt = retrieve(source)
                if not attempt      : continue
                if attempt == 'stop':
                    if tries < 5:
                        continue
                    else:
                        logger.info('Finished {toyear} (presumably)'.format(**locals()))
                        break
                
                tries = 0
                yield {'raw_content': attempt, 'identifier':target, 'source': source }


def retrieve(url, iteration=1):
    try:
        content = requests.get(url)
        if content.status_code == 200 and '404.htm' not in content.url :
            return content.text
        if content.status_code == 404 or '404.htm' in content.url :
            logger.info('No page found: {url}'.format(**locals()))
            return 'stop'
    except Exception, err:
        if iteration < 3:
            logger.warning('Unable to retrieve, attempting again {url} ({iteration})'.format(**locals()))
            retrieve(url, iteration+1)
        else:
            logger.warning('Unable to retrieve {url}, due to {err} --> skipping'.format(**locals()))
            return False

                

    
