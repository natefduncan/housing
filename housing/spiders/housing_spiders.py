#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 20:28:18 2018

SCRAPING HOUSING DATA

@author: User
"""

import scrapy
import os
import unicodedata as uc
import time
import numpy as np
from pathlib import Path
import datetime as dt

#FOR SELENIUM

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pyvirtualdisplay import Display

#FOR SPLASH

#import docker
#from scrapy_splash import SplashRequest

def get_address(x): #Gets address from returned html string. 
    output = []
    if len(x.split('\n')[0]) == 0:
        y = x.split('\n')[1].split(' ')
    else:
        y = x.split('\n')[0].split(' ')
    for i in y:
        if i != '':
            output.append(i)
    return " ".join(output)

path = Path(os.path.dirname(os.path.abspath(__file__)))
os.chdir(str(path))

def flatten(x): #List of lists to list. 
    temp = []
    for i in x:
        if isinstance(i, list):
            for j in i:
                temp.append(j)
        else: temp.append(i)
    return temp

def ucode(x): #Changes Unicode to ASCII.
    if isinstance(x, unicode):
        return uc.normalize('NFKD', x).encode('ascii', 'ignore')

def list_of_lists(x, n): #Turns a list into a list of lists. 
    i=0
    new_list=[]
    while i<len(x):
        new_list.append(x[i:i+n])
        i+=n
    return new_list
    
def get_ints(x): #Gets only the numbers from a string. 
    output = []
    for p in x:
        try:
            float(p)
            output.append(p)
        except:
            pass
    return "".join(output)

def remove_comma(x):
    output = []
    for i in x:
        if i != ",":
            output.append(i)
    return "".join(output)


class homie(scrapy.Spider):
    
    name = "realtor"
    
    def __init__(self):
        
        #FOR SPLASH
        
        #client = docker.from_env()
        #client.containers.run("scrapinghub/splash", detach = True)
        
        #FOR SELENIUM
        
        self.driver = webdriver.Firefox()
        #self.driver.set_window_size(1920, 1080)
        '''
        #start Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            self.driver = webdriver.Chrome(chrome_options=options)
        except:
            pass
        '''
    def start_requests(self):
        areas = ["Dallas_TX", "Frisco_TX"]
        base = "https://www.realtor.com/realestateandhomes-search/"
        for i in areas:
          counter = 1
          try:
            url = (base+i+("/pg-%s") % str(counter))
            print(url)
            yield scrapy.Request(url=url, callback = self.parse)
            time.sleep(10)
          except:
            self.driver.close()
            
    def parse(self, response):
        self.driver.get(response.url)
        
        cards_path = "//html/body/div[5]/div[2]/div/div[1]/div[2]/section/div[2]/ul/li[contains(@class, 'component_property-card js-component_property-card js-quick-view')]"
        
        try:
            element = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, cards_path))
            )
        except:
            self.driver.close()
        
        response = scrapy.Selector(text=self.driver.page_source)
        rows = response.xpath(cards_path)
        values = []
        counter = 1 #Don't know why this is.
        for i in rows:
          link_path = cards_path + ("[%s]/div[3]/div[1]/a/@href" % str(counter))
          link = response.xpath(link_path).extract()[0]
          base = "https://www.realtor.com/"
          link = base + link
          now = dt.datetime.now()
          file_name = "realtor_urls_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".txt"
          with open(file_name, "a+") as file:
            file.write(link)
            print("Added: " + link)
          counter += 1
            

class zillow(scrapy.Spider):
    
    name = "zillow"
    
    start_urls = [
        'https://www.zillow.com/dallas-tx',
        'https://www.zillow.com/Frisco-tx',
        'https://www.zillow.com/carrolton-tx',
        'https://www.zillow.com/prosper-tx'
        ]
    
    def __init__(self):

        #FOR SELENIUM
        
        #display = Display(visible=0, size=(800, 600))
        #display.start()
        
        self.driver = webdriver.Firefox()
        
        #self.driver.set_window_size(1920, 1080)
        
        #Start Headless Chrome
        '''
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        
        try:
            self.driver = webdriver.Chrome(chrome_options=options)
        except:
            pass
        '''
    
    
    def parse(self, response):
        
        self.driver.get(response.url)

        time.sleep(np.random.uniform(2, 5, 1))
        
        def wait_for(condition_function):
            start_time = time.time()
            while time.time() < start_time + 3:
                if condition_function():
                    return True
                else:
                    time.sleep(0.1)
            raise Exception(
                'Timeout waiting for {}'.format(condition_function.__name__)
            )
        
        def click_through_to_new_page(link_object):
            self.driver.execute_script("arguments[0].click();", link_object)
        
            def link_has_gone_stale():
                try:
                    # poll the link with an arbitrary call
                    link_object.find_elements_by_id('doesnt-matter') 
                    return False
                except:
                    return True
        
            wait_for(link_has_gone_stale)
        
        go = True 
        
        while go:
            response = scrapy.Selector(text=self.driver.page_source)
            
            if not bool(response.xpath('//li[@class = "zsg-pagination-next"]/a')):
                go = False
            
            if go: 
                nxt = self.driver.find_element_by_xpath('//li[@class = "zsg-pagination-next"]/a')
            
            x = response.xpath('//article[starts-with(@id, "zpid")]')
        
            values = []
            
            for i in x:
                photos = i.xpath('div[1]/a/@href').extract()
                photos = [ucode(t) for t in photos]
                specs = i.xpath('div[1]/div[1]/p/span/text()').extract()
                specs = [remove_comma(ucode(j)) for j in specs]
                while len(specs) != 6:
                    specs.append("NaN")
                values.append([photos, specs])
            
            values = [flatten(n) for n in values]
            
            #Write the values to txt file. 
            
            filename = "texas.txt"
            f = open(filename, 'a+')
    
            for m in values:
                f.write("%s\n" % m)
            f.close()
            
            if go:
                click_through_to_new_page(nxt) 
                time.sleep(2)
                
        self.driver.close()
        
class trulia(scrapy.Spider):
    
    name = "trulia"
    
    def __init__(self):

        #FOR SELENIUM
        
        self.driver = webdriver.Firefox()
        #self.driver.set_window_size(1920, 1080)
        
        #Start Headless Chrome
        '''
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        
        try:
            self.driver = webdriver.Chrome(chrome_options=options)
        except:
            pass
        '''
    def start_requests(self):
    
        base = "https://www.trulia.com"
         
        yield scrapy.Request(url=base, callback = self.parse)
            
    def parse(self, response):
        
        self.driver.get(response.url)
        
        areas = ["SLC, UT", "Logan, UTAH", 'St. George, UT', 'Cedar City, UT', 'West Jordan, UT']
        
        try:
            element = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, 'searchBox'))
            )
        except:
            self.driver.close()
        
        search = self.driver.find_element_by_id('searchBox')
        search.clear()
        search.send_keys("Utah")
        button = self.driver.find_element_by_xpath('//body/div[2]/div/div[1]/div/div/div[2]/button')
        button.click()
        
        for i in areas: 
            
            try:
                element = WebDriverWait(self.driver, 60).until(
                    EC.presence_of_element_located((By.ID, 'locationInputs'))
                )
            except:
                self.driver.close()
            
            #Enters value into the search bar. 
            search = self.driver.find_element_by_id('locationInputs')
            search.clear()
            search.send_keys(i)
            button = self.driver.find_element_by_id("dropdownBtn")
            button.click()
            
            try:
                element = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/section/div[3]/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li'))
                )
            except:
                self.driver.close()
            
            response = scrapy.Selector(text=self.driver.page_source)
            
            x = response.xpath('/html/body/section/div[3]/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li')
            
            values = []
            
            for i in x:
                price = i.xpath('div/div/div[2]/a[1]/div[2]/div/div[1]/span/text()').extract()
                address1 = i.xpath('div/div/div[2]/a[2]/div/div[1]/text()').extract()
                address2 = i.xpath('div/div/div[2]/a[2]/div/div[2]/div/text()').extract()
                bed = i.xpath('div/div/div[2]/a[1]/div[2]/div/div[2]/ul/li[1]/text()').extract()
                bath = i.xpath('div/div/div[2]/a[1]/div[2]/div/div[2]/ul/li[2]/text()').extract()
                sq_ft = i.xpath('div/div/div[2]/a[1]/div[2]/div/div[2]/ul/li[3]/text()').extract()
                
                values.append([price, address1, address2, bed, bath, sq_ft])
            
            values = [flatten(n) for n in values]
            
            #Write the values to txt file. 
            
            filename = "trulia_data.txt"
            f = open(filename, 'a+')
    
            for m in values:
                f.write("%s\n" % m)
            f.close()
        

        
        
