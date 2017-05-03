# -*- coding: utf-8 -*-
"""
Created on Wed May  3 14:33:16 2017

@author: damian
"""

import re
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

class vk_paywall():

    def getlink(self, link):
        '''modifies the link to the article to bypass the cookie wall'''
        link=re.sub("/$","",link)
        link="http://www.volkskrant.nl//cookiewall/accept?url="+link
        return link 
        
    def gotologin(self):
        self.driver = webdriver.Firefox(firefox_profile=None)
        self.driver.get(self.getlink('http://www.volkskrant.nl'))
        self.driver.implicitly_wait(5)
        element = self.driver.find_element_by_class_name("nav-section__text")
        element.click()
        self.driver.implicitly_wait(6)
        self.driver.switch_to_active_element()
        actions = ActionChains(self.driver)
        actions.click()
        actions.perform()
        #self.driver.implicitly_wait(5)
        #actions = ActionChains(self.driver)
        #
        #actions.perform()
        
    def login(self,username,password):
        actions = ActionChains(self.driver)
        #actions.click()
        actions.send_keys(username)
        actions.send_keys(Keys.TAB)
        actions.perform()
        sleep(3)
        #self.driver.implicitly_wait(2)
        #actions = ActionChains(self.driver)        
        actions2 = ActionChains(self.driver)
        actions2.send_keys(password)
        actions2.perform()
        sleep(2)
        
        actions3 = ActionChains(self.driver)
        actions3.send_keys(Keys.ENTER)
        actions3.perform()



if __name__ == '__main__':
    myscraper = vk_paywall()
    myscraper.gotologin()
    sleep(5)
    myscraper.login(USERNAME,PASSWORD)
