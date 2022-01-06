# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "raywhite_com"

	total_count = 0

	start_urls = ['https://www.raywhite.com/contact/?type=People&target=people&suburb=Parramatta%2C+NSW+2150&radius=50&firstname=&lastname=&_so=contact',
				  'https://www.raywhite.com/contact/?type=People&target=people&suburb=Brisbane%2C+QLD+4000&radius=50&firstname=&lastname=&_so=contact',
				  'https://www.raywhite.com/contact/?type=People&target=people&suburb=Nerang%2C+QLD+4211&radius=50&firstname=&lastname=&_so=contact',
				  'https://www.raywhite.com/contact/?type=People&target=people&suburb=Nambour%2C+QLD+4560&radius=50&firstname=&lastname=&_so=contact',
				  'https://www.raywhite.com/contact/?type=People&target=people&suburb=Melbourne%2C+VIC+3000&radius=50&firstname=&lastname=&_so=contact',
				  'https://www.raywhite.com/contact/?type=People&target=people&suburb=Adelaide%2C+SA+5000&radius=50&firstname=&lastname=&_so=contact',
				  'https://www.raywhite.com/contact/?type=People&target=people&suburb=Perth%2C+WA+6000&radius=50&firstname=&lastname=&_so=contact']

	use_selenium = False

	got_urls = []
	result_data_list = {}
	filepath = 'raywhite_com.xlsx'
	headers = ['name', 'company', 'agent role', 'email', 'mobile','phone', 'street-address', 'locality', 'region', 'postal-code', 'country-name', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):

		for url in self.start_urls:
			yield scrapy.Request(
				url=url,
				callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})
			# break

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################

	def parseProductList(self, response):
		products_list = response.xpath('//div[@class="card horizontal-split vcard"]/figure/a/@href').extract()
		for p in products_list:
			if p in self.got_urls:
				continue
			self.got_urls.append(p)
			yield scrapy.Request(url=response.urljoin(p), callback=self.parseProduct, dont_filter=True)
			# break

	def parseProduct(self, response):
		pro = response

		item = OrderedDict()
		for h in self.headers:
			item[h] = ''
		item['name'] = pro.xpath('.//hgroup[@class="pageheading"]/h1/text()').extract_first()
		company = pro.xpath('.//hgroup[@class="pageheading"]/p/text()').extract_first()
		if company:
			company = company.split(',')
			if len(company) > 1:
				item['company'] = company[1]
				item['agent role'] = company[0]
			else:
				item['company'] = company[0]
				item['agent role'] = pro.xpath('.//ul[@class="indented-icons"]/li[@class="role"]/text()').extract_first()

		email = pro.xpath('.//ul[@class="indented-icons"]/li[@class="email"]/a/text()').extract_first()
		item['email'] = email

		mob = pro.xpath('.//ul[@class="indented-icons"]/li[@class="tel mob item"]/a/text()').extract_first()
		item['mobile'] = mob

		phone = pro.xpath('.//ul[@class="indented-icons"]/li[@class="tel ph item"]/a/text()').extract_first()
		item['phone'] = phone

		item['street-address'] = pro.xpath('.//li[@class="adr"]/span[@class="street-address"]/text()').extract_first()
		item['locality'] = pro.xpath('.//li[@class="adr"]/span[@class="locality"]/text()').extract_first()
		item['region'] = pro.xpath('.//li[@class="adr"]/span[@class="region"]/text()').extract_first()
		item['postal-code'] = pro.xpath('.//li[@class="adr"]/span[@class="postal-code"]/text()').extract_first()
		item['country-name'] = pro.xpath('.//li[@class="adr"]/span[@class="country-name"]/text()').extract_first()

		# item['mobile'] = pro.
		item['detail url'] = response.url
		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item




