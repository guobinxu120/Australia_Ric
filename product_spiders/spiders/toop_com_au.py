# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "toop_com_au"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'toop_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'phone']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.toop.com.au/contactus.asp#sec3',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="person-container"]')

			if not products_list:
				return
			for pro in products_list:
				name = pro.xpath('./div[@class="person-name"]/h3/text()').extract_first()
				agent_role = pro.xpath('./div[@class="person-name"]/p/text()').extract_first()
				mail = pro.xpath('./div[@class="person-contact-details"]/a[@class="tooltip-person"]/span/text()').extract_first()
				phone = pro.xpath('./div[@class="person-contact-details"]/a[@class="tooltip-person tpt-person-phone"]/@title').extract_first()

				item = OrderedDict()

				for h in self.headers:
					item[h] = ''

				item['name'] = name

				item['agent role'] = agent_role
				item['email'] = mail
				item['phone'] = phone

				self.total_count += 1
				print('total_count: ' + str(self.total_count))
				print item
				self.result_data_list[str(self.total_count)] = item

				# url = pro.xpath('./a/@href').extract_first()
				# if url:
				# 	if 'http' not in url:
				# 		url = response.urljoin(url)
                #
				# 	name = pro.xpath('./h4[@id="mlk-11"]/text()').extract_first()
				# 	company = pro.xpath('./h4[@id="mlk-14"]/text()').extract_first()
				# 	yield scrapy.Request(
				# 			url=url,
				# 			callback=self.parseProduct, dont_filter=True,
				# 		meta={
				# 			'name':name,
				# 			'company':company
				# 		})
				# break
		except:

			i = 1
			i += 1

		# page_num = response.meta['page_num'] + 1
		# yield scrapy.Request(
		# 	url='https://www.peterblackshaw.com.au/find-an-agent.html?offset=' + str(page_num * 12),
		# 	callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//h1[@id="mlk-4"]/text()').extract_first()
		company = response.meta['company']
		item['company'] = response.xpath('//div[@id="mlk-15"]/text()').extract_first()

		item['agent role'] = response.xpath('//h3[@id="mlk-5"]/text()').extract_first()

		# phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		# item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		socials = response.xpath('//div[@class="verticalbox-cell"]/div/table/tr')
		for so in socials:
			label = so.xpath('./td/div[@class="label"]/text()').extract_first()
			if not label:
				continue
			if 'Phone' in label:
				item['direct number'] = so.xpath('./td/a[@itemprop="telephone"]/text()').extract_first()
			elif 'Mobile' in label:
				item['mobile'] = so.xpath('./td/a[@itemprop="telephone"]/text()').extract_first()
			elif 'Fax' in label:
				item['fax'] = so.xpath('./td/div[@itemprop="faxNumber"]/text()').extract_first()

		email = response.xpath('//a[@itemprop="email"]/@href').extract_first()
		if email:
			item['email'] = email.replace('mailto:', '')

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="fluidgrid-group fluidgrid-group-none"]//div[@class="fluidgrid-cell fluidgrid-cell-4"]/div/div/text()').extract()
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








