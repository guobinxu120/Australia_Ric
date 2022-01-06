# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "ruralcoproperty_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'ruralcoproperty_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'phone', 'address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.ruralcoproperty.com.au/agent-results/?agent_name=',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="row no-gutters"]/div[@class="col-md-6"]/div/div[@class="agents-bg"]/a')

			if not products_list:
				return
			for pro in products_list:
				url = pro.xpath('./@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					# name = pro.xpath('./h4[@id="mlk-11"]/text()').extract_first()
					# company = pro.xpath('./h4[@id="mlk-14"]/text()').extract_first()
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True)
				# break
		except:

			i = 1
			i +=1

		if response.meta['page_num'] == 26:
			return
		page_num = response.meta['page_num'] + 1
		yield scrapy.Request(
			url='https://www.ruralcoproperty.com.au/agent-results/?agent_name=&pageno=' + str(page_num),
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//div[@class="agents-name"]/text()').extract_first()
		# company = response.meta['company']
		# item['company'] = response.xpath('//div[@id="mlk-15"]/text()').extract_first()

		item['agent role'] = response.xpath('//p[@class="text-muted agents-post"]/text()').extract_first()

		item['address'] = response.xpath('//div[@class="agents-info info"]/ul/li/span/text()').extract_first()

		# phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		# item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		socials = response.xpath('//div[@class="agents-info info"]/ul/li/a/@href').extract()
		for label in socials:
			# label = so.xpath('./td/div[@class="label"]/text()').extract_first()
			if not label:
				continue
			if 'tel:' in label:
				item['phone'] = label.replace('tel:', '')
			elif 'mailto:' in label:
				item['email'] = label.replace('mailto:', '')

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="agent-details"]//p/text()').extract()
		if profiles:
			abouts = []
			for ppp in profiles:
				if ppp:
					ppp = ppp.strip()
					if ppp:
						abouts.append(ppp)
			if abouts:
				item['about us'] = '\n'.join(abouts)
		item['detail url'] = response.url

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item

		# yield item
		# yield item








