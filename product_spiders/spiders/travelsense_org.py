# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class travelsense_org_spider(scrapy.Spider):

	name = "travelsense_org"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'travelsense_org1.xlsx'
	headers = ['name', 'agent role', 'email', 'phone', 'website', 'facebook', 'linkedin', 'twitter', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(travelsense_org_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		url = 'https://www.travelsense.org/api-search/?add%5B%5D=&travelspecialty%5B%5D=&language%5B%5D=&rating%5B%5D=' \
			  '&brand%5B%5D=&zip=&orderBy=nameasc&pageSize=10&pageNumber=50'
		yield scrapy.Request(
			url=url,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		products_list = response.xpath('//div[contains(@id,"agentIndex-")]//a[@class="btn btn-primary"]/@href').extract()

		if not products_list:
			return
		for product in products_list:
			yield scrapy.Request(
			url='https://www.travelsense.org' + product,
			callback=self.parseProduct, dont_filter=True)

			# break

		response.meta['page_num'] += 1
		next_url = 'https://www.travelsense.org/api-search/?add%5B%5D=&travelspecialty%5B%5D=&language%5B%5D=&rating%5B%5D=&brand%5B%5D=&zip=&orderBy=nameasc&pageSize=10&pageNumber=' + str(response.meta['page_num'])
		if next_url:
			yield scrapy.Request(
				url=next_url,
				callback=self.parseProductList, dont_filter=True, meta=response.meta)

	def parseProduct(self, response):
		name = response.xpath('//div[@id="profileContent"]/h4/text()').extract_first()
		role = response.xpath('//div[@id="profileContent"]/h5/text()').extract_first()
		# address = '\n'.join(response.xpath('./tr[2]/td[1]//text()').extract())

		data = response.xpath('//div[@id="profileContent"]/h5//text()').extract()
		mail = data[-1]
		phone = data[-3].strip()

		socials = response.xpath('//div[@id="profileContent"]/ul[@class="list-inline social-media-list"]/li/a/@href').extract()
		face = ''
		linked = ''
		site = ''
		twitter = ''
		for so in socials:
			if 'facebook.com' in so:
				face = so
			elif 'linkedin.com' in so:
				linked = so
			elif 'twitter.com' in so:
				twitter = so
			elif 'instagram' in so:
				instagram = so
			else:
				site = so

		url = response.url

		item = OrderedDict()
		for h in self.headers:
			item[h] = ''

		item['name'] = name
		item['agent role'] = role
		item['email'] = mail
		item['phone'] = phone
		item['website'] = site
		item['facebook'] = face
		item['linkedin'] = linked
		item['twitter'] = twitter
		item['detail url'] = url

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item








