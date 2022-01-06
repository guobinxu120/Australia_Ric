# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class independentyoganetwork_org_spider(scrapy.Spider):

	name = "independentyoganetwork_org"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'independentyoganetwork_org.xlsx'
	headers = ['name', 'location', 'email', 'phone', 'website', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(independentyoganetwork_org_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		url = 'https://www.independentyoganetwork.org/teachers'
		yield scrapy.Request(
			url=url,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		products_list = response.xpath('//div[@class="teacher-listing"]/div/a/@href').extract()

		if not products_list:
			return
		for product in products_list:
			yield scrapy.Request(
			url=response.urljoin(product),
			callback=self.parseProduct, dont_filter=True)

			# break

		response.meta['page_num'] += 1
		next_url = 'https://www.independentyoganetwork.org/teachers?site=' + str(response.meta['page_num'])
		if next_url:
			yield scrapy.Request(
				url=next_url,
				callback=self.parseProductList, dont_filter=True, meta=response.meta)

	def parseProduct(self, response):
		span_tags = response.xpath('//div[@class="teacher-contacts"]/p/span')
		name = response.xpath('//h1[@class="teacher-name"]/text()').extract_first()
		location = ''
		phone = ''
		site = ''
		for i, span_tag in enumerate(span_tags):
			label = span_tag.xpath('./text()').extract_first()
			if 'Telephone' in label:
				phone = span_tags[i + 1].xpath('./text()').extract_first()
			elif 'Location' in label:
				location = span_tags[i + 1].xpath('./text()').extract_first()
		if name:
			url = response.url

			mail = response.xpath('//div[@class="teacher-contacts"]/p/a[text()="email"]/@href').extract_first()
			mail = mail.replace('mailto:', '')
			site = response.xpath('//div[@class="teacher-contacts"]/p/a[text()="website"]/@href').extract_first()

			item = OrderedDict()
			for h in self.headers:
				item[h] = ''

			item['name'] = name
			item['location'] = location
			item['email'] = mail
			item['phone'] = phone
			item['website'] = site
			item['detail url'] = url

			self.total_count += 1
			print('total_count: ' + str(self.total_count))
			print item
			self.result_data_list[str(self.total_count)] = item








