from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time

def getreactions(data):

    options = Options()
    options.set_headless(True)
    driver = webdriver.Firefox(options = options)

    for entry in data:
        fb = entry['facebooksite']
        driver.get(fb)
        time.sleep(5)
        reacts = driver.find_elements_by_xpath('//span[@class="_2u_j"]')
       
        reactions = []
        for i in reacts:
            reactions.append(i.text)

        def add_s(x):
            if x.endswith("s")==False:
                x+="s"
            return(x)

        reactions = [add_s(x) for x in reactions] 
        recs = {k:v for v,k in [s.split(' ') for s in reactions]}

        units = {"K":1000,"M":1000000}
        result= {}

        for k,v in recs.items(): 
            try:
                result[k] = float(v) 
            except ValueError: 
                unit=v[-1]
                v=float(v[:-1])
                result[k] = v*units[unit]

        for k,v in result.items():
            result[k] = int(v)

        needed =  ['Likes', 'Shares', 'Comments']
        for k in needed:
            if k not in result:
                result[k] = 0

            print("Fetched reactions.")
            entry.update(result)
    driver.close()
    return(data)    
