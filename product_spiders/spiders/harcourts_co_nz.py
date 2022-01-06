# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "harcourts_co_nz"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'harcourts_com_au.xlsx'
	headers = ['name', 'office', 'agent role', 'email', 'mobile', 'phone', 'website']
###########################################################

	got_urls = []

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		letters = ['a', 'b', 'c', 'd', 'e', 'f',
				   'g', 'h', 'i', 'j', 'k', 'l',
				   'm', 'n', 'o', 'p', 'q', 'r',
				   's', 't', 'u', 'v', 'w', 'x',
				   'y', 'z']
		# letters = ['a']

		for l in letters:
			url = 'https://harcourts.com.au/Staff/Search/?agentName={}&locationName=&locationID='.format(l)

			yield scrapy.Request(
				url=url,
				callback=self.parseProductList, dont_filter=True, meta={'url':url, 'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="agent_info"]')

			if not products_list:
				return
			for pro in products_list:

				item = OrderedDict()
				for h in self.headers:
					item[h] = ''

				detail_url = pro.xpath('./a/@href').extract_first()
				if detail_url in self.got_urls:
					continue

				self.got_urls.append(detail_url)

				item['name'] = pro.xpath('./a/h2/text()').extract_first()

				# agent_role = pro.xpath('./p[@class="agent-thumb-contact title left"]/text()').extract_first()
				# if agent_role:
				# 	agent_role = agent_role.strip()
				# item['agent role'] = agent_role

				# email = pro.xpath('.//span[@class="agent-thumb-email"]/text()').extract_first()
				# item['email'] = email

				agent_cards = pro.xpath('./p/a')
				for agent_card in agent_cards:
					if agent_card.xpath('./@class').extract_first() == 'mobile-number':
						item['mobile'] = agent_card.xpath('./@href').extract_first().replace('tel:', '')
					elif agent_card.xpath('./@class').extract_first() == 'my-website':
						item['website'] = agent_card.xpath('./@href').extract_first()
					elif 'mailto:' in agent_card.xpath('./@href').extract_first():
						item['email'] = agent_card.xpath('./@href').extract_first().replace('mailto:', '')

				# self.total_count += 1
				# print('total_count: ' + str(self.total_count))
				# print item
				# self.result_data_list[str(self.total_count)] = item

				yield scrapy.Request(url='https://harcourts.com.au' + detail_url, callback=self.parseItem, dont_filter=True, meta={'item': item})



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

		response.meta['page_num'] = response.meta['page_num'] + 1
		print('page count: ' + str(response.meta['page_num']))

		next_url = response.meta['url'] + '&pageIndex=' + str(response.meta['page_num'])
		if next_url:
			yield scrapy.Request(response.urljoin(next_url), self.parseProductList, dont_filter=True, meta=response.meta)


	def parseItem(self, response):
		item = response.meta['item']
		role = response.xpath('//div[@class="detailName has-photo"]/h2/text()').extract_first()
		if role:
			role = role.strip()
		item['agent role'] = role

		office = response.xpath('//div[@class="detailOffice"]/a/text()').extract_first()
		if office:
			office = office.strip()
		item['office'] = office

		detailNumbers = response.xpath('//div[@class="detailNumbers"]/div')
		for num_tag in detailNumbers:
			name = num_tag.xpath('./span/text()').extract()
			if 'Mobile:' in name:
				item['mobile'] = num_tag.xpath('./a/text()').extract_first()
			elif 'Phone:' in name:
				item['phone'] = num_tag.xpath('./a/text()').extract_first()
			elif 'Email:' in name:
				item['email'] = num_tag.xpath('./a/text()').extract_first()
			elif 'Web:' in name:
				item['website'] = num_tag.xpath('./a/text()').extract_first()

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item









