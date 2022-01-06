# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "nzsothebysrealty"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'nzsothebysrealty_com.xlsx'
	headers = ['name', 'company', 'agent role', 'email', 'phone', 'cell phone']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):


		yield scrapy.Request(
			url='https://www.nzsothebysrealty.com/our-people/',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="col-xs-6 thumb"]/div/div[@class="agent-thumb-content"]')

			if not products_list:
				return
			for pro in products_list:

				item = OrderedDict()
				for h in self.headers:
					item[h] = ''
				item['name'] = pro.xpath('./p[@class="agent-thumb-name"]/a/text()').extract_first()
				company = pro.xpath('./p[@class="agent-thumb-oname clear"]/text()').extract_first()
				if company:
					company = company.strip()
				item['company'] = company

				agent_role = pro.xpath('./p[@class="agent-thumb-contact title left"]/text()').extract_first()
				if agent_role:
					agent_role = agent_role.strip()
				item['agent role'] = agent_role

				email = pro.xpath('.//span[@class="agent-thumb-email"]/text()').extract_first()
				item['email'] = email

				agent_cards = pro.xpath('./p[@class="agent-thumb-contact"]')
				for agent_card in agent_cards:
					temps = agent_card.xpath('./span//text()').extract()
					if len(temps) > 1:
						if 'Cell Phone' in temps[0]:
							item['cell phone'] = temps[1]
						elif 'Phone' in temps[0]:
							item['phone'] = temps[1]
				self.total_count += 1
				print('total_count: ' + str(self.total_count))
				print item
				self.result_data_list[str(self.total_count)] = item



				# url = pro.xpath('./a/@href').extract_first()
				# if url:
				# 	# url = url.replace('https://www.bellecommercial.com', '')
				# 	if 'http' not in url:
				# 		url = response.urljoin(url)
				# 	yield scrapy.Request(
				# 			url=url,
				# 			callback=self.parseProduct, dont_filter=True, meta={'name': name,
				# 																'agent_role': agent_role,
				# 																'email': email})
				# else:
				# 	self.total_count += 1
				# 	print('total_count: ' + str(self.total_count))
				# 	# print item
				# 	self.result_data_list[str(self.total_count)] = item
				# break
		except:

			i = 1
			i +=1

			return

		page_num = response.meta['page_num'] + 1
		print('page count: ' + str(page_num))
		next_url = response.xpath('//a[@class="block page-right page-left-right"]/@href').extract_first()
		if next_url:
			yield scrapy.Request(response.urljoin(next_url), self.parseProductList, dont_filter=True, meta={'page_num': page_num})







