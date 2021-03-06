#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 20:28:18 2018

SCRAPING HOUSING DATA

@author: User
"""

#Changes

import scrapy #Framework for scraping
from scrapy import Selector
import os #For working with files
import unicodedata as uc #Unicode to string
import time #For pausing code
import numpy as np #For working with arrays
from pathlib import Path #For working with system independent paths
import datetime as dt #For working with and converting times
import math #For some math functions
import pandas as pd #For working with dataframes
from random import randint #To set random delays
from time import sleep #For pausing code
from  more_itertools import unique_everseen #Ordered uniques

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
    
path = Path(os.path.dirname(os.path.abspath(__file__)))
os.chdir(str(path))

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n] #list to list of lists
        
def check_equal(lst): #checks that all the values are the same in a list.
   return lst[1:] == lst[:-1]

def parse_price(x): #For Realtor
    x  = "".join(x)
    return get_ints(x.replace("\n", "").replace(",", "").replace(" ", "").replace("$", "").replace(r"\u", ""))
    
def parse_address(x): #For Realtor
    output = []
    for i in x:
        j = i.replace(",", "").replace("\n", "").replace(r"\u", "").strip()
        if j != "": 
            output.append(j)
    if len(output) > 4:
      output[0] = "".join([output[0], " ", output[1]])
      del output[1]
    if len(output) < 4:
      for i in range(0, 4 - len(output)):
        output.append("")
    return output

def parse_top(x, labels): #For Realtor
    '''
    options:
    beds, baths, sq ft, sqft lot, acres lot, 3 full, 2 half baths
    '''
    chunk_counter = 1
    for i in range(0, len(x)):
      if check_equal(list(chunks(x, chunk_counter))):
        break
      else:
        chunk_counter += 1
    
    beds = ""
    baths = ""
    half_baths = ""
    sq_ft = ""
    sqft_lot = ""
    acres_lot = ""
    
    temp = [i.replace("\n", "").replace(",", "").replace(r"\u", "").strip() for i in x]
    temp = [i for i in temp if i != ""]
    temp = temp[:chunk_counter]
    
    labels = [i.replace("\n", "").replace(",", "").replace(r"\u", "").strip() for i in labels]
    labels = [i for i in labels if i != ""]
    labels = labels[:chunk_counter]
    
    for i in range(0, len(temp)):
      lab = labels[i]
      if lab == "beds":
          beds = temp[i]
      elif lab == "full":
          baths = temp[i]
      elif lab == "baths":
          baths = temp[i]
      elif lab == "half baths":
          half_baths = temp[i]
      elif lab == "sq ft":
          sq_ft = temp[i]
      elif lab == "sqft lot":
          sqft_lot = temp[i]
      elif lab == "acres lot":
          acres_lot = temp[i]
    
    return [beds, baths, half_baths, sq_ft, sqft_lot, acres_lot]

def parse_bottom(x): #For Realtor
    '''
    status, price/sq_ft,on realtor, type, built, style, description
    '''
    
    status = ""
    price_sq_ft = ""
    on_realtor = ""
    tp = ""
    built = ""
    
    mx = max([len(i) for i in x])
    
    for i in range(0, len(x)):
        temp = x[i]
        temp = temp.replace("\n", "").replace(",", "").replace(r"\u", "").strip()
        if temp == "Status":
            status = x[i+1].replace("\n", "").replace(",", "").replace(r"\u", "").strip()
        elif temp == "Price/Sq Ft":
            price_sq_ft = x[i+1].replace("\n", "").replace(",", "").replace("$","").replace(r"\u", "").strip()
        elif temp == "On realtor.com":
            on_realtor = x[i+1].replace("\n", "").replace(",", "").replace(r"\u", "").strip()
        elif temp == "Type":
            tp = x[i+1].replace("\n", "").replace(",", "").replace(r"\u", "").strip()
        elif temp == "Built":
            built = x[i+1].replace("\n", "").replace(",", "").replace(r"\u", "").strip()
    return [status, price_sq_ft, on_realtor, tp, built]

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

class realtor(scrapy.Spider):
  name = "realtor"
  
  def start_requests(self):
    areas = ["Dallas-County_TX", "Collin-County_TX", "Denton-County_TX", "Rockwall-County_TX", "Hunt-County_TX", "Tarrant-County_TX", 
    "Johnson-County_TX", "Ellis-County_TX", "Kaufman-County_TX"]
    base = "https://www.realtor.com/realestateandhomes-search/"
    for i in areas:
      url = base + i
      yield scrapy.Request(url=url, callback=self.parse, meta={'area' : i})
  
  def parse(self, response):
    request = scrapy.Selector(response)
    area = response.meta['area']
    pages_path = "//*[@id='search-result-count']/text()"
    pages = int(math.ceil(int(get_ints(response.xpath(pages_path).extract()[0])) / float(43.8)))
    base = "https://www.realtor.com/realestateandhomes-search/"
    counter = 1
    while counter < pages:
      url = (base+area+("/pg-%s") % str(counter))
      yield scrapy.Request(url=url, callback=self.parse2)
      counter += 1
      
  def parse2(self, response):
    request = scrapy.Selector(response)
    urls = request.xpath("//li[contains(@class, 'component_property-card js-component_property-card js-quick-view')]/@data-url").extract()
    urls = [link.encode('utf-8').strip() for link in urls]
    base_url = "https://www.realtor.com"
    urls = [base_url + link for link in urls]
    now = dt.datetime.now()
    file_name = "realtor_urls_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".txt"
    for link in urls:
      with open(file_name, "a+") as file:
        file.write(link)
        file.write("\n")
        print("Added: " + link)

class realtor_data(scrapy.Spider):

  name = "realtor_data"
  
  def start_requests(self):
    now = dt.datetime.now()
    #file_name = "realtor_urls_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".txt"
    file_name = "realtor_urls_2019.4.5.txt"
    
    with open(file_name) as f:
      urls = f.readlines()
    # you may also want to remove whitespace characters like `\n` at the end of each line
    urls = [x.strip().replace("\n", "") for x in urls]
    
    #pd_file_name = "realtor_data_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".csv"
    pd_file_name = "realtor_data_2019.4.5.csv"
    
    columns = ["date_scraped", "url", "address", "city", "state", "zip", "price", "beds", "baths", "half_baths", "sq_ft", "sqft_lot", "acres_lot", "status", "price_sq_ft", "on_realtor", "type", "built", "style", "description"]
    df = pd.DataFrame(columns=columns)
    try:
      df = pd.read_csv(pd_file_name)
      urls = [i for i in urls if i not in df.url.tolist()]
    except:
      pass
    
    print("REMAINING: " + str(len(urls)) + str(len(df)) + ("-" * 30))
    
    for url in urls:
        yield scrapy.Request(url=url, callback=self.parse)
    
  def parse(self, response):
    now = dt.datetime.now()
    #pd_file_name = "realtor_data_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".csv"
    pd_file_name = "realtor_data_2019.4.5.csv"
    
    columns = ["date_scraped", "url", "lat", "lon", "address", "city", "state", "zip", "price", "beds", "baths", "half_baths", "sq_ft", "sqft_lot", "acres_lot", "status", "price_sq_ft", "on_realtor", "type", "built", "style", "description"]
    df = pd.DataFrame(columns=columns)
    try:
      df = pd.read_csv(pd_file_name)
    except:
      pass
    url = response.request.url
    
    counter = 1
    request = scrapy.Selector(response)
    
    block_xpath = "//h2[@class='title-section-detail']/text()" #'Blocked IP Address'
    price_xpath = "//input[@id='price']/@value"
    price2_xpath = "//input[@id='home_price']/@value"
    info_xpath = "//ul[contains(@class, 'property-meta list-horizontal list-style-disc list-spaced')]/li/span/text()"
    info_labels_xpath = "//ul[contains(@class, 'property-meta list-horizontal list-style-disc list-spaced')]/li/text()"
    address_xpath = "//input[@id='full_address_display']/@value"
    city_xpath = "//input[@id='city']/@value"
    state_xpath = "//input[@id='state']/@value"
    zip_xpath = "//meta[@itemprop='postalCode']/@content"
    lat_xpath = "//meta[@itemprop='latitude']/@content"
    lon_xpath = "//meta[@itemprop='longitude']/@content"
    items_xpath = "//li[@class='ldp-key-fact-item']/div/text()"
    style_xpath = "//a[@data-omtag='ldp:propInfo:listingStyle']/text()"
    desc_xpath = "//p[@id='ldp-detail-romance']/text()"
    
    #Block
    block = request.xpath(block_xpath).extract()
    #Price
    if len(request.xpath(price_xpath).extract())>0:
      price = get_ints(request.xpath(price_xpath).extract()[0])
    elif len(request.xpath(price2_xpath).extract())>0:
      price = get_ints(request.xpath(price2_xpath).extract()[0])
    else:
      price = ""
    #Tops
    vals = request.xpath(info_xpath).extract()
    labs = request.xpath(info_labels_xpath).extract()
    top = parse_top(vals, labs)
    if top[1]=="" and top[2]=="": #For when half baths
      bath_xpath = "//span[contains(@class, 'data-value property-half-baths')]/text()"
      if len(request.xpath(bath_xpath).extract())>1:
        top[1] = request.xpath(bath_xpath).extract()[0]
        top[2] = request.xpath(bath_xpath).extract()[1]
    #Address
    if request.xpath(address_xpath).extract() > 0:
      try:
        address = request.xpath(address_xpath).extract()[0].encode('utf-8').strip()
      except:
        address = ""
      try:
        city = address.split(",")[1]
      except:
        city = ""
      try:
        state = address.split(",")[2].strip().split(" ")[0]
      except:
        state = ""
      try:
        zip_code = get_ints(address.split(",")[2])
      except:
        zip_code = ""
      try:
        address = address.split(",")[0]
      except:
        address = ""
      full_address = [address, city, state, zip_code]
    else:
      full_address = ["", "", "", ""]
    #Latitude, Longitude
    lat = request.xpath(lat_xpath).extract()[0]
    lon = request.xpath(lon_xpath).extract()[0]
    #Items
    items = parse_bottom(request.xpath(items_xpath).extract())
    #Style
    if len(request.xpath(style_xpath).extract())>1:
      style = ",".join(request.xpath(style_xpath).extract())
    elif len(request.xpath(style_xpath).extract())==0:
      style = ""
    else:
      style = request.xpath(style_xpath).extract()
    #Description
    if len(request.xpath(desc_xpath).extract())>1:
      desc = ",".join(request.xpath(desc_xpath).extract())
    elif len(request.xpath(desc_xpath).extract())==1:
      desc = request.xpath(desc_xpath).extract()
    else:
      desc = ""

    output = [block, dt.datetime.strftime(now, "%m/%d/%Y"), url, lat, lon, full_address, price, top, items, style, desc]
    output = flatten(output)
    for i in range(0, len(output)):
      try:
        output[i] = output[i].encode('utf-8').strip()
      except:
        pass
        
    print(output)
    print(len(output))
    print(len(columns))
    df.loc[len(df)] = output
    
    if counter == 5:
      df.to_csv(pd_file_name, index = False)
      counter = 1
    else:
      counter += 1
    
    df.to_csv(pd_file_name, index = False)
    
class homefinder(scrapy.Spider):
    
    name = "homefinder"
    start_urls = [
        'https://www.homefinder.com'
    ]
    
    def __init__(self):
        
        #FOR SPLASH
        
        #client = docker.from_env()
        #client.containers.run("scrapinghub/splash", detach = True)
        
        #FOR SELENIUM
        self.driver = webdriver.Firefox()
        
        #self.driver.set_window_size(1920, 1080)
        '''
        perhaps try chrome
        #start Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            self.driver = webdriver.Chrome(chrome_options=options)
        except:
            pass
        '''
            
    def parse(self, response):
        areas = ["TX/Dallas"]
        base = "https://homefinder.com/for-sale/"
        for j in areas:
          page_counter = 1
          pages = 100
          while page_counter <= pages:
            print("-" * 30)
            print(page_counter)
            print(pages)
            print("-" * 30)
            url = (base+j+("?pg=%s") % str(page_counter))
            self.driver.get(url)
            time.sleep(5)
        
            pages_path = "/html/body/div[1]/div[2]/div/section/div[2]/div[4]/div/div[1]/div/div[40]/nav/ul/li[6]/a/text()"
            cards_path = ("/html/body/div[1]/div[2]/div/section/div[2]/div[4]/div/div[1]/div/div")
            
            try:
                element = WebDriverWait(self.driver, 120).until(
                    EC.presence_of_element_located((By.XPATH, cards_path))
                )
            except:
                self.driver.close()
            
            response = scrapy.Selector(text=self.driver.page_source)
            
            #Get the actual number of pages. 
            pages = get_ints(response.xpath(pages_path).extract())

            rows = response.xpath(cards_path)
            
            counter = 1 
            for i in rows:
              link = i.xpath("a/@href").extract()
              link.enc
              link = link.encode('utf-8').strip()
              if link[0] == "/":
                base_url = "https://www.realtor.com"
                link = base_url + link
                now = dt.datetime.now()
                file_name = "homefinder_urls_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".txt"
                with open(file_name, "a+") as file:
                  file.write(link)
                  file.write("\n")
                  print("Added: " + link)
          page_counter += 1
          print("finished")

class homefinder_data(scrapy.Spider):
  name = "homefinder_data"
  start_urls = [
        'https://www.realtor.com'
    ]
    
  def __init__(self):
    self.driver = webdriver.Firefox()
    
  def parse(self, response):
    
    now = dt.datetime.now()
    #file_name = "realtor_urls_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".txt"
    file_name = "realtor_urls_2019.3.11.txt"
    with open(file_name) as f:
      urls = f.readlines()
      # you may also want to remove whitespace characters like `\n` at the end of each line
      urls = [x.strip().replace("\n", "") for x in urls]
    
    #pd_file_name = "realtor_data_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".csv"
    pd_file_name = "realtor_data_2019.3.11.csv"
    
    columns = ["date_scraped", "url", "address", "city", "state", "zip", "price", "beds", "baths", "half_baths", "sq_ft", "sqft_lot", "acres_lot", "status", "price_sq_ft", "on_realtor", "type", "built", "style", "description"]
    df = pd.DataFrame(columns=columns)
    try:
      df = pd.read_csv(pd_file_name)
      urls = [i for i in urls if i not in df.url.tolist()]
    except:
      pass
      
    counter = 1
    
    for url in urls:
      self.driver.get(url)
      description_wait_xpath = "//*[@id='ldp-detail-overview']//text()"
      description_xpath = "//*[@id='ldp-detail-overview']//text()"

      try:
          element = WebDriverWait(self.driver, 120).until(
              EC.presence_of_element_located((By.XPATH, description_wait_xpath))
          )
      except:
          self.driver.close()
          
      response = scrapy.Selector(text=self.driver.page_source)
      price_xpath = "/html/body/div[5]/div[4]/div[2]/div[2]/div/section[1]/div[1]/div[2]/div[1]/div/div[1]/div/div//text()"
      address_xpath = "/html/body/div[5]/div[4]/div[2]/div[2]/div/section[1]/div[1]/div[2]/div[2]/div/div[2]/div/h1//text()"
      top_info_xpath = "/html/body/div[5]/div[4]/div[2]/div[2]/div/section[1]/div[1]/div[2]/div[2]/div/div[1]/ul/li//text()"
 
      output = [dt.datetime.strftime(now, "%m/%d/%Y"), url, parse_address(response.xpath(address_xpath).extract()), parse_price(response.xpath(price_xpath).extract()), parse_top(response.xpath(top_info_xpath).extract()), parse_bottom(response.xpath(description_xpath).extract())]
      output = flatten(output)
      for i in range(0, len(output)):
        try:
          output[i] = output[i].encode('utf-8').strip()
        except:
          pass
          
      print(output)
      print(len(output))
      print(len(columns))
      df.loc[len(df)] = output
      
      if counter == 5:
        df.to_csv(pd_file_name, index = False)
        counter = 1
      else:
        counter += 1
      
    df.to_csv(pd_file_name, index = False)    
    
class zillow(scrapy.Spider):
    
    name = "zillow"
        
    def start_requests(self):
      areas = ["https://www.zillow.com/homes/for_sale/Denton-County-TX/pmf,pf_pt/988_rid/globalrelevanceex_sort/33.259647,-96.673165,32.889101,-97.16755_rect/10_zm/",
      "https://www.zillow.com/homes/for_sale/Dallas-County-TX/pmf,pf_pt/978_rid/globalrelevanceex_sort/33.136976,-96.283494,32.393297,-97.272263_rect/10_zm/"]
      for i in areas:
        for j in range(1, 21):
          url = i + "%s_p" % (str(j))
          yield scrapy.Request(url=url, callback=self.parse)
    
    def parse(self, response):
      print("RESPONSE-------")
      url_xpath = "//div[contains(@class, 'zsg-photo-card-content zsg-aspect-ratio-content')]/a[contains(@href, 'homedetails')]/@href"
      request = scrapy.Selector(response)
      print(request.xpath(url_xpath))
      urls = request.xpath(url_xpath).extract()
      now = dt.datetime.now()
      file_name = "zillow_urls_" + str(now.year) + "." + str(now.month) + "."  + str(now.day) + ".txt"
      for link in urls:
        with open(file_name, "a+") as file:
          file.write(link)
          file.write("\n")
          print("Added: " + link)
        
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
        areas = ["/TX/Dallas"]
        for i in areas:
          yield scrapy.Request(url=base+i, callback = self.parse)
            
    def parse(self, response):
        
        self.driver.get(response.url)
        
        cards_path = '/html/body/section/div[5]/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[1]/ul/li'
        try:
            element = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located((By.XPATH, cards_path))
            )
        except:
            self.driver.close()
        
        sleep(randint(0,7))
        
        response = scrapy.Selector(text=self.driver.page_source)
        
        links_xpath = "//body//a[@class='tileLink']/@href"
        
        links = response.xpath(links_xpath)
        
        for i in links:
          print(i)
        

        
        
