# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class yogatherapy_org_au_spider(scrapy.Spider):

	name = "yogatherapy_org_au"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'yogatherapy_org_au.xlsx'
	headers = ['name', 'city', 'state', 'email', 'website', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(yogatherapy_org_au_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		url = 'http://yogatherapy.org.au/find-a-therapist-2/'
		yield scrapy.Request(
			url=url,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		products_list = response.xpath('//div[@class="pmpro_member_directory-item"]')

		if not products_list:
			return
		for product in products_list:
			name = product.xpath('./h3[@class="pmpro_member_directory_display-name"]/a/text()').extract_first()
			mail = product.xpath('./p[@class="pmpro_member_directory_email"]//text()').extract()
			if len(mail) > 2:
				mail = mail[2].strip()
			else:
				mail = ''
			site = product.xpath('./p[@class="pmpro_member_directory_user_url"]/a/@href').extract_first()

			city = product.xpath('./p[@class="pmpro_member_directory_pmpro_bcity"]//text()').extract()
			if len(city) > 2:
				city = city[2].strip()
			else:
				city = ''

			state = product.xpath('./p[@class="pmpro_member_directory_pmpro_bstate"]//text()').extract()
			if len(state) > 2:
				state = state[2].strip()
			else:
				state = ''


			item = OrderedDict()
			for h in self.headers:
				item[h] = ''

			item['name'] = name
			item['city'] = city
			item['state'] = state
			item['email'] = mail
			item['website'] = site
			item['detail url'] = product.xpath('./h3[@class="pmpro_member_directory_display-name"]/a/@href').extract_first()

			self.total_count += 1
			print('total_count: ' + str(self.total_count))
			print item
			self.result_data_list[str(self.total_count)] = item

			# break

		response.meta['page_num'] += 1
		next_url = response.xpath('//span[@class="pmpro_next"]/a/@href').extract_first()
		if next_url:
			yield scrapy.Request(
				url=next_url,
				callback=self.parseProductList, dont_filter=True, meta=response.meta)