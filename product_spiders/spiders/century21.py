# -*- coding: utf-8 -*-
import scrapy, csv
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "century21_2121"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'century21.xlsx'
	headers = ['name', 'office', 'agent role', 'email', 'mobile', 'phone', 'website', 'detail url']
###########################################################

	got_urls = []

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################


	def start_requests(self):
			url = 'https://www.century21.com.au/sitemap/real-estate-agents/nsw'

			yield scrapy.Request(
				url=url,
				callback=self.parseProductList, dont_filter=True, meta={'url':url, 'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//ul[@class="searchResults grid-1 grid-sml-2 grid-med-3 grid-print-3"]/li//a[text()="Visit Website"]/@href').extract()

			if not products_list:
				return
			for pro in products_list:
				if '=undefined' in pro:
					continue
				# pro = 'http://totalrealestate.century21.com.au'
				yield scrapy.Request(url=pro + '/our-team', callback=self.parseItemPersonList, dont_filter=True, errback=self.errCall)
				# break


		except:

			i = 1
			i +=1

			return

		# response.meta['page_num'] = response.meta['page_num'] + 1
		# print('page count: ' + str(response.meta['page_num']))
        #
		# next_url = response.meta['url'] + '&pageIndex=' + str(response.meta['page_num'])
		# if next_url:
		# 	yield scrapy.Request(response.urljoin(next_url), self.parseProductList, dont_filter=True, meta=response.meta)
	def errCall(self, re):
		i = 0
		i += 1
		return


	def parseItemPersonList(self, response):
		urls = response.xpath('//a[@class="agent-image block"]/@href').extract()
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parseItem, dont_filter=True)
			# break

	def parseItem(self, response):

		if 'missing' in response.url:
			yield {'url': response.meta['url']}
			return


		item = OrderedDict()
		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//h1[@class="super"]/text()').extract_first()
		item['agent role'] = response.xpath('//span[@class="jobtitle"]/text()').extract_first()
		item['office'] = response.xpath('//span[@class="officename"]/text()').extract_first()
		if item['office']:
			item['office'] = item['office'].replace('// ', '').strip()

		data = response.xpath('//div[@class="content-container"]/div[@class="oneline"]')
		for d in data:
			name = d.xpath('./abbr/text()').extract_first()
			if 'Mobile' in name:
				item['mobile'] = d.xpath('./a/text()').extract_first()
			elif 'Phone' in name:
				item['phone'] = d.xpath('./a/text()').extract_first()
			elif 'Email' in name:
				item['email'] = d.xpath('./a/text()').extract_first()

		item['detail url'] = response.url

		# item = response.meta['item']
		# role = response.xpath('//div[@class="detailName has-photo"]/h2/text()').extract_first()
		# if role:
		# 	role = role.strip()
		# item['agent role'] = role
        #
		# office = response.xpath('//div[@class="detailOffice"]/a/text()').extract_first()
		# if office:
		# 	office = office.strip()
		# item['office'] = office
        #
		# detailNumbers = response.xpath('//div[@class="detailNumbers"]/div')
		# for num_tag in detailNumbers:
		# 	name = num_tag.xpath('./span/text()').extract()
		# 	if 'Mobile:' in name:
		# 		item['mobile'] = num_tag.xpath('./a/text()').extract_first()
		# 	elif 'Phone:' in name:
		# 		item['phone'] = num_tag.xpath('./a/text()').extract_first()
		# 	elif 'Email:' in name:
		# 		item['email'] = num_tag.xpath('./a/text()').extract_first()
		# 	elif 'Web:' in name:
		# 		item['website'] = num_tag.xpath('./a/text()').extract_first()

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item









