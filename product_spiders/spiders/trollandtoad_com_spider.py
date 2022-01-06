# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse


class trollandtoad_com_Spider(scrapy.Spider):

	name = "trollandtoad_com_spider"

	total_count = 0
	result_data_list = {}
	headers = ['Main Category Link', 'ProductLink', 'ProductTitle', 'Set', 'Image URL']
###########################################################

	def __init__(self, *args, **kwargs):
		super(trollandtoad_com_Spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		filename = "basic_data/categories_tt.txt"
		with open(filename, 'U') as f:
			for category_url in f.readlines():

				cat_name = category_url.split('/')[3]
				self.result_data_list[cat_name] = []

				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parseProductList, meta={'cat': cat_name, 'cat_url': category_url.strip()})

		########--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.theoutnet.com/en-au/shop/just-in',
		# 			callback=self.parseProductList)
		#################################################

	def parseProductList(self, response):
		products_list = response.xpath('//div[@class="cat_result_wrapper"]')
		for product in products_list:
			item = OrderedDict()

			for h in self.headers:
				item[h] = ''
			item['Main Category Link'] = response.url
			item['ProductLink'] = response.urljoin(product.xpath('./div[@class="cat_result_text"]/h2/a/@href').extract_first())
			item['ProductTitle'] = product.xpath('./div[@class="cat_result_text"]/h2/a/text()').extract_first()
			item['Set'] = product.xpath('.//a[@class="cat_result_category_link"]/text()').extract_first()
			item['Image URL'] = product.xpath('.//img[@class="CategoryProductThumb"]/@src').extract_first()

			condition_xpaths = product.xpath('./form')
			for i, f in enumerate(condition_xpaths):
				n = i + 1
				if 'Condition{}'.format(n) not in self.headers:
					self.headers.append('Condition{}'.format(n))
				if 'Qty{}'.format(n) not in self.headers:
					self.headers.append('Qty{}'.format(n))
				if 'Price{}'.format(n) not in self.headers:
					self.headers.append('Price{}'.format(n))

				item['Condition{}'.format(n)] = ''.join(f.xpath('.//td[@class="condition_text"]//text()').extract())

				qty = f.xpath('.//td[@class="condition_qty"]/text()').re(r'[\d\+]+')
				if qty:
					qty = qty[0]
				else:
					qty = ''

				item['Qty{}'.format(n)] = qty
				item['Price{}'.format(n)] = f.xpath('.//td[@class="price_text"]/text()').extract_first()

			self.total_count += 1
			# print 'total_count: ' + str(self.total_count)
			# print item
			self.result_data_list[response.meta['cat']].append(item)
			# yield item
		next_nums = response.xpath('//a[@rel="next"]/@onclick').re(r'[\d.,]+')
		if next_nums:
			basic_url = '{}?orderBy=Alphabetical+A-Z&filterKeywords=&sois=Yes&minPrice=&maxPrice=&pageLimiter=25&showImage=Yes&PageNum={}'.format(response.meta['cat_url'], next_nums[0])
			yield Request(response.urljoin(basic_url), callback=self.parseProductList, meta=response.meta)







