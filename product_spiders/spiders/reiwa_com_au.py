# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "reiwa_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'reiwa_com_au.xlsx'
	headers = ['name', 'email', 'phone', 'website', 'facebook', 'address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):

		yield scrapy.Request(
			url='https://reiwa.com.au/agent-finder/',
			callback=self.parse1, dont_filter=True, meta={'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################
	def parse1(self, response):
		products_list = response.xpath('//div[@id="agent-az-content"]/ul/li/a/@href').extract()
		for url in products_list:
			yield scrapy.Request(
				url=response.urljoin(url),
				callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})
			# break

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="agent-result-container"]')

			if not products_list:
				return
			for pro in products_list:
				name = pro.xpath('.//div[@class="address"]/a/h3/text()').extract_first()
				url = pro.xpath('./div/div/div/a/@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True, meta={'name':name})
				# break
		except:

			i = 1
			i +=1

			return
		next_url = response.xpath('//ul[@class="pagination"]/li[@class="active"]/following-sibling::*[1]/a/@href').extract_first()
		if next_url:
			yield scrapy.Request(response.urljoin(next_url), self.parseProductList, dont_filter=True)


	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.meta['name']

		datas = response.xpath('//div[@class="col-xs-12 col-md-8 col-sm-8"]/div')
		for d in datas:
			name = d.xpath('./div/strong/text()').extract_first()
			if not name:
				values = d.xpath('./div[@id="ctl00_uxContentHolder_dzMainTop_uxColumnDisplay_ctl00_uxControlColumn_ctl00_uxWidgetHost_uxWidgetHost_widget_ctl00_pnlAbout"]/span/text()').extract()
				if values:
					val_list = []
					for v in values:
						if v:
							v = v.strip()
							if v:
								val_list.append(v)
					val = ''
					if val_list:
						val = '\n'.join(val_list)
					item['about us'] = val
			else:
				if name == 'Address':
					values = d.xpath('./div/text()').extract()
					val_list = []
					for v in values:
						if v:
							v = v.strip()
							if v:
								val_list.append(v)
					val = ''
					if val_list:
						val = ' '.join(val_list)
					item['address'] = val
				elif name == 'Phone':
					value = d.xpath('./div/a/@data-telephone-number').extract_first()
					item['phone'] = value
				elif name == 'Website':
					value = d.xpath('./div/a/@href').extract_first()
					item['website'] = value
				elif name == 'Facebook':
					value = d.xpath('./div/a/@href').extract_first()
					item['facebook'] = value

		profiles = response.xpath('//div[@class="ibox-content article"]/p/text()').extract()
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








