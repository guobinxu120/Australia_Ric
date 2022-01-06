# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "mcgrath_com_spider"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	headers = ['name', 'agent role', 'email', 'mobile', 'direct number', 'website', 'streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'Profile', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):


				yield scrapy.Request(
					url='https://www.firstnational.com.au/agents',
					callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.firstnational.com.au/json/data/agents/?&gallery&limit=12&pg={}'.format(str(2)),
		# 			callback=self.parseProductList, meta={'page_num': 2})
		# ################################################

	def parseProductList(self, response):

		if response.meta['page_num'] == 1:
			products_list = response.xpath('//div[@class="pure-u-1 pure-u-md-1-2 agent"]/div')

			if not products_list:
				return
			for pro in products_list:

				item = OrderedDict()
				for h in self.headers:
					item[h] = ''
				item['name'] = pro.xpath('./div[@class="pure-u-2-3 detail"]/h4/strong/text()').extract_first()
				item['agent role'] = pro.xpath('./div[@class="pure-u-2-3 detail"]/p/text()').extract_first()
				item['mobile'] = pro.xpath('./div[@class="pure-u-2-3 detail"]/p/a/text()').extract_first()


				url = pro.xpath('./div[@class="pure-u-2-3 detail"]/p[@class="link"]/a/@href').extract_first()
				if url:
					# url = url.replace('https://www.bellecommercial.com', '')
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True, meta={'item': item})
				else:
					self.total_count += 1
					print('total_count: ' + str(self.total_count))
					# print item
					self.result_data_list[str(self.total_count)] = item
		else:
			# if not response.xpath('//pre/text()').extract_first():
			# 	return
			try:
				products_list = loads(response.text)['data']['agents']

				if not products_list:
					return
				for pro in products_list:

					item = OrderedDict()
					for h in self.headers:
						item[h] = ''
					item['name'] = pro['full_name']
					item['agent role'] = pro['staff_position']
					item['email'] = pro['staff_email']
					item['mobile'] = pro['staff_mobile']
					item['direct number'] = pro['staff_phone']


					url = pro['url']
					if url:
						# url = url.replace('https://www.bellecommercial.com', '')
						if 'http' not in url:
							url = response.urljoin(url)
						yield scrapy.Request(
								url=url,
								callback=self.parseProduct, dont_filter=True, meta={'item': item})
					else:
						self.total_count += 1
						print('total_count: ' + str(self.total_count))
						# print item
						self.result_data_list[str(self.total_count)] = item
					# break
			except:
				return




			page_num = response.meta['page_num'] + 1
			next_url = 'https://www.firstnational.com.au/json/data/agents/?&gallery&limit=12&pg={}'.format(str(page_num))
			yield scrapy.Request(next_url, self.parseProductList, dont_filter=True, meta={'page_num': page_num})


	def parseProduct(self, response):


		item = response.meta['item']

		# for h in self.headers:
		# 	item[h] = ''
		site = response.xpath('//p/a[@target="_blank"]/text()').extract_first()
		if site:
			if 'http' in site:
				item['website'] = site
		item['email'] = response.xpath('//a[@itemprop="email"]/text()').extract_first()
		item['direct number+'] = response.xpath('//span[@itemprop="telephone"]/text()').extract_first()
		item['streetAddress'] = response.xpath('//p/span[@itemprop="streetAddress"]/text()').extract_first()
		item['addressLocality'] = response.xpath('//p/span[@itemprop="addressLocality"]/text()').extract_first()
		item['addressRegion'] = response.xpath('//p/span[@itemprop="addressRegion"]/text()').extract_first()
		item['postalCode'] = response.xpath('//p/span[@itemprop="postalCode"]/text()').extract_first()

		profiles = response.xpath('//div[@class="pure-u-1 pure-u-md-2-3 left-col"]/div/p/text()').extract()
		if profiles:
			item['Profile'] = '\n'.join(profiles)
		item['detail url'] = response.url

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item

		# yield item
		# yield item








