# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class tours_com_spider(scrapy.Spider):

	name = "tours_com"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'tours_com.xlsx'
	headers = ['name', 'agent role', 'office_name', 'email', 'phone', 'fax', 'website', 'address', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(tours_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.tours.com/travel_agents.htm',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})

	def parseProductList(self, response):
		products_list = response.xpath('//div[contains(@class,"p ")]/table')

		if not products_list:
			return
		for product in products_list:
			names = product.xpath('./tr[1]/td[1]//text()').extract()
			name = ''
			company = ''
			if len(names) > 1:
				name = names[0]
				company = names[1]
			else:
				name = names[0]

			role = product.xpath('./tr[1]/td[2]//text()').extract_first()
			address = '\n'.join(product.xpath('./tr[2]/td[1]//text()').extract())

			mail = product.xpath('./tr[2]/td[2]/script/text()').extract_first()
			if mail:
				mail = mail.replace("'+'", '').replace('mailto:', '').split('href="')[-1].split('"')[0]
			site = product.xpath('./tr[2]/td[2]/a/@href').extract_first()

			phones = product.xpath('./tr[2]/td[3]//text()').extract()
			phone = ''
			fax = ''
			if len(phones) > 3:
				phone = phones[1]
				fax = phones[3]
			else:
				phone = phones[1]
			if phone:
				phone = phone.strip()
			if fax:
				fax = phone.strip()

			url = response.url

			item = OrderedDict()
			for h in self.headers:
				item[h] = ''

			item['name'] = name
			item['agent role'] = role
			item['office_name'] = company
			item['email'] = mail
			item['phone'] = phone
			item['fax'] = fax
			item['website'] = site
			item['address'] = address
			item['detail url'] = url

			self.total_count += 1
			print('total_count: ' + str(self.total_count))
			print item
			self.result_data_list[str(self.total_count)] = item

		next_url = response.xpath('//a[text()="Next"]/@href').extract_first()
		if next_url:
			response.meta['page_num'] += 1
			next_url = 'https://www.tours.com/travel_agents.htm?pg=' + str(response.meta['page_num'])
			yield scrapy.Request(
				url=next_url,
				callback=self.parseProductList, dont_filter=True, meta=response.meta)






