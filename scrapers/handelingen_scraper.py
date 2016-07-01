import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from core.database import check_exists
import logging

logger = logging.getLogger(__name__)

START_URL = "https://zoek.officielebekendmakingen.nl/actueel/30"
BASE_URL  = "https://zoek.officielebekendmakingen.nl/"

class kamerhandelingen_scraper(Scraper):
    """Scrapes Dutch parlementairy and senate proceedings """
    
    
    def get(self):
        '''Document collected from officielebekendmakingen.nl by scraping 'bladeren' section  '''

        self.doctype = "Kamerhandelingen NL"
        self.version = ".1"
        self.date    = datetime.datetime(year=2016, month=6, day=28)
        
        time_url = START_URL
        while time_url:
            time_page = requests.get(time_url)
            time_dom  = fromstring(time_page.text)
            time_dom.make_links_absolute(BASE_URL)
            next_url = time_dom.xpath('//div[@class="sub-lijst"]//a[contains(text(),"Handelingen")]/@href')
            if next_url:
                next_url = next_url[0]
                logger.debug("@{next_url}".format(**locals()))
                while next_url: 
                    home = requests.get(next_url)
                    DOM_home = fromstring(home.text)
                    DOM_home.make_links_absolute(BASE_URL)
                    for item_link in DOM_home.xpath('//div[@class="lijst"]//li//@href'):
                        _id = item_link.split('/')[-1].split('.')[0]
                        if check_exists(_id)[0]: continue
                        item_page = requests.get(item_link)
                        item_dom  = fromstring(item_page.text)
                        item_dom.make_links_absolute(BASE_URL)

                        metadata_url = item_dom.xpath('//*[contains(text(), "Technische informatie")]/@href')
                        xml_url      = item_dom.xpath('//*[contains(text(), "Xml-formaat")]/@href')

                        if xml_url:
                            xml_content = requests.get(xml_url[0]).text
                            if metadata_url:
                                metadata_page = requests.get(metadata_url[0])
                                metadata_dom  = fromstring(metadata_page.text)

                                metadata = dict(
                                    zip(
                                        metadata_dom.xpath('//tr/td[1]//text()'),
                                        metadata_dom.xpath('//tr/td[2]//text()')
                                    ))
                        else:
                            metadata = {}
                            
                        doc = dict(
                            _id         = _id,
                            source      = item_link,
                            xml_content = xml_content
                        )
                        doc.update(metadata)
                        yield doc

                    next_url = DOM_home.xpath('//a[.="Volgende"]/@href')
                    if next_url:
                        next_url = next_url[0]
                    time_url = DOM_home.xpath('//div[@id="Paging"]//a[@class="vorige"]/@href')
                    logging.debug("at {home.url}, following time: {time_url}".format(**locals()))
                    if time_url:
                        time_url = time_url[0]


            
if __name__=="__main__":
    kamerhandelingen_scraper().get()
