from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from scrapy.http import TextResponse
from scrapy.exceptions import CloseSpider
from scrapy import signals
from datetime import date
import json
import time

class SeleniumMiddleware(object):

    def __init__(self, s):
        # self.exec_path = s.get('PHANTOMJS_PATH', './phantomjs.exe')
        self.exec_path = 'D:/chromedriver.exe'

###########################################################

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler.settings)

        crawler.signals.connect(obj.spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(obj.spider_closed,
                                signal=signals.spider_closed)
        return obj

###########################################################

    def spider_opened(self, spider):
        try:
            self.d = init_driver(self.exec_path)
        except TimeoutException:
            CloseSpider('PhantomJS Timeout Error!!!')

###########################################################

    def spider_closed(self, spider):
        self.d.quit()
###########################################################
    
    def process_request(self, request, spider):
        if spider.use_selenium:
            print "############################ Received url request from scrapy #####"

            try:
                if 'https://www.bigginscott.com.au/missing' == request.url:
                    pass

                self.d.get(request.url)
                

            except TimeoutException as e:            
                raise CloseSpider('TIMEOUT ERROR')
            
            if 'https://www.bigginscott.com.au/missing' == self.d.current_url:
                    pass

            resp1 = TextResponse(url=self.d.current_url,
                                body=self.d.page_source,
                                encoding='utf-8')
            resp1.request = request.copy()
            
            return resp1

###########################################################
###########################################################

def init_driver(path):
    d = webdriver.Chrome(executable_path=path)
    d.set_page_load_timeout(120)

    return d