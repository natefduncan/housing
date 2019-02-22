#General packages
import scrapy
import numpy as np
import os
import time
import random
from pathlib import Path

path = Path(os.path.dirname(os.path.abspath(__file__)))
os.chdir(str(path))

#Selenium packages
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

class proxy(scrapy.Spider):
    name = "proxy"
    custom_settings = {"DOWNLOADER_MIDDLEWARES" : {}}
    
    def start_requests(self):
        urls = ["https://us-proxy.org/"]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
    
    def __init__(self):
        self.driver = webdriver.Firefox()
        
    def parse(self, response):
        self.driver.get(response.url)
        response = scrapy.Selector(text=self.driver.page_source)
        
        table_xpath = ("//body/section/div[@class='container']/"
                       "div[@class='table-responsive']/div[@id='proxylisttable_wrapper']/"
                       "div[2]/div[1]/table/tbody/tr")
        
        proxies = []
        
        for i in response.xpath(table_xpath):
            proxies.append(str(i.xpath("td[1]/text()").extract()[0]) + ":" + str(i.xpath("td[2]/text()").extract()[0]))

        filename = "proxy_list.txt"
        f = open(filename, 'w+')
        
        for m in proxies:
            print(m)
            f.write("%s\n" % m)
        f.close()
        
        self.driver.close()
