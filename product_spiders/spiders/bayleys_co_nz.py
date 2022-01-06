# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "bayleys_co_nz"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'bayleys_co_nz.xlsx'
	headers = ['name', 'company', 'agent role', 'email', 'mobile', 'office number', 'facebook', 'linkedin']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):


		yield scrapy.Request(
			url='https://www.bayleys.co.nz/search?SearchType=Residential&Radius=6&ListingType=None&OrderType=IsFeatured&Page=1&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//section[@id="agentGallery"]/div/div[@class="col-sm-6 col-md-4 col-lg-3"]/div')

			if not products_list:
				return
			for pro in products_list:

				item = OrderedDict()
				for h in self.headers:
					item[h] = ''
				item['name'] = pro.xpath('.//div[@data-mh="agent-name"]/h3/text()').extract_first()
				company = pro.xpath('.//div[@data-mh="agent-name"]/h4/text()').extract_first()
				if company:
					company = company.strip()
				item['company'] = company

				agent_role = pro.xpath('.//div[@data-mh="agent-name"]/h5/text()').extract_first()
				if agent_role:
					agent_role = agent_role.strip()
				item['agent role'] = agent_role

				email = pro.xpath('.//a[@itemprop="email"]/text()').extract_first()
				item['email'] = email

				linkedin = pro.xpath('.//a[@class="text-linkedin"]/@href').extract_first()
				item['linkedin'] = linkedin

				facebook = pro.xpath('.//a[@class="text-facebook"]/@href').extract_first()
				item['facebook'] = facebook
				# item['mobile'] = pro.xpath('.//a[@itemprop="email"]/text()').extract_first()
				# item['direct number'] = pro['staff_phone']
				agent_cards = pro.xpath('.//div[@data-mh="agent-card"]/table/tbody/tr')
				for agent_card in agent_cards:
					temps = agent_card.xpath('./td//text()').extract()
					if len(temps) > 1:
						if 'Mobile' in temps[0]:
							item['mobile'] = temps[1]
						elif 'Office' in temps[0]:
							item['office number'] = temps[1]
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
		next_url = 'https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page={}&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12'.format(str(page_num))
		yield scrapy.Request(next_url, self.parseProductList, dont_filter=True, meta={'page_num': page_num})







