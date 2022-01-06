# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class iyengaryoga_org_uk_spider(scrapy.Spider):

	name = "iyengaryoga_org_uk"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'iyengaryoga_org_uk.xlsx'
	headers = ['name', 'agent role', 'email', 'phone', 'website', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(iyengaryoga_org_uk_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		url = 'https://iyengaryoga.org.uk/teacher-search/?country_id=GB&firstname=&surname=&postcode=&distance=-1&county=&submit=Submit'
		yield scrapy.Request(
			url=url,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		products_list = response.xpath('//div[@class="iyengar-teacher-search-col-right"]/div[@class="userpro-awsm"]/div[@class="userpro-awsm-pic"]/a/@href').extract()

		if not products_list:
			return
		for product in products_list:
			yield scrapy.Request(
			url=product,
			callback=self.parseProduct, dont_filter=True)

			# break

		response.meta['page_num'] += 1
		next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract_first()
		if next_url:
			yield scrapy.Request(
				url=next_url,
				callback=self.parseProductList, dont_filter=True, meta=response.meta)

	def parseProduct(self, response):
		profile_tags = response.xpath('//ul[@class="wppb-profile"]/li')
		name = ''
		mail = ''
		phone = ''
		site = ''
		for profile_tag in profile_tags:
			h1 = profile_tag.xpath('./h1/text()').extract_first()
			if h1:
				name = h1
			else:
				label = profile_tag.xpath('./label/text()').extract_first()
				if label:
					if 'Email' in label:
						mail = profile_tag.xpath('./span/a/text()').extract_first()
					elif 'Phone' in label:
						phone = profile_tag.xpath('./span/text()').extract_first()
					elif 'Website' in label:
						site = profile_tag.xpath('./span/a/text()').extract_first()
		if name:
			url = response.url

			item = OrderedDict()
			for h in self.headers:
				item[h] = ''

			item['name'] = name
			item['email'] = mail
			item['phone'] = phone
			item['website'] = site
			item['detail url'] = url

			self.total_count += 1
			print('total_count: ' + str(self.total_count))
			print item
			self.result_data_list[str(self.total_count)] = item








