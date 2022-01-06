# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse


class trollandtoad_com_Spider(scrapy.Spider):

	name = "yoox_com_spider"

	total_count = 0
	result_data_list = {}
	result_data_list['men'] = []
	result_data_list['women'] = []
	headers = ['Product link', 'Brand Name', 'Product Name', 'Product Type', 'Description', 'Current Price', 'Product Code', 'Image1', 'Image2', 'Image3', 'category']
###########################################################

	def __init__(self, *args, **kwargs):
		super(trollandtoad_com_Spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		filename = "basic_data/categories_yoox.txt"
		with open(filename, 'U') as f:
			for category_url in f.readlines():

				cat_name = category_url.split('/')[3]

				cat_name = 'men'
				if 'women' in category_url:
					cat_name = 'women'
				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parseProductList, meta={'cat': cat_name, 'cat_url': category_url.strip()})

		########--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.theoutnet.com/en-au/shop/just-in',
		# 			callback=self.parseProductList)
		#################################################

	def parseProductList(self, response):
		products_urls = response.xpath('//div[@class="col-8-24"]//a[@class="itemlink"]/@href').extract()
		for url in products_urls:
			# yield Request(response.urljoin(url), self.finalparse, meta=response.meta)
			yield Request('https://www.yoox.com/au/46593412BR/item#cod10=46593412BR&sizeId=1&sizeName=ONESIZE', self.finalparse, meta=response.meta)
			break
		# next_url = response.xpath('//li[@class="next-page"]/a/@href').extract_first()
		# if next_url:
		# 	yield Request(response.urljoin(next_url), self.parseProductList, meta=response.meta)
	def finalparse(self, response):

		item = OrderedDict()

		# for h in self.headers:
		# 	item[h] = ''
		item['Product link'] = response.url
		item['Brand Name'] = ''
		brand = response.xpath('//div[@id="itemTitle"]//a[@data-tracking-label="brand"]/text()').extract_first()
		if brand:
			item['Brand Name'] = brand.strip()

		item['Product Name'] = response.xpath('//div[@id="itemTitle"]/div[@class="text-size-l-plus margin-half-bottom"]/text()').extract_first()
		item['Product Type'] = ''
		type = response.xpath('//div[@id="itemTitle"]//a[@data-tracking-label="category"]/text()').extract_first()
		if type:
			item['Product Type'] = type.strip()
		item['Description'] = response.xpath('//div[@class="info-col-1 item-info-column col-1-2"]/ul').extract_first()
		item['Current Price'] = response.xpath('//span[@itemprop="price"]/text()').extract_first()
		item['Product Code'] = response.xpath('//span[@id="itemInfoCod10"]/text()').extract_first()
		colors = response.xpath('//li[contains(@class,"colorsize-elm")]/img')
		images = response.xpath('//img[@data-tracking-label="change photo"]/@src').extract()
		if not images:
			images = response.xpath('//div[@class="item-image"]/img/@src').extract()
		for color_tag in colors:
			item['Color'] = color_tag.xpath('./@alt').extract_first()
			id = color_tag.xpath('./parent::li/@id').extract_first()
			id = id.replace('color', '').strip()
			for i, img in enumerate(images):
				if i > 2: break
				if '_9_' in img:
					img = img.replace('_9_', '_12_')
				img = img.replace(img.split('/')[-1].split('_')[0], id.lower())
				item['Image{}'.format(i+1)] = img
			if item['Product Code'].lower() != id.lower():
				item['Product Code'] = id
			item['category'] = response.meta['cat']
			new_item = OrderedDict()
			for key in item.keys():
				new_item[key] = item[key]
			yield item

			self.result_data_list[response.meta['cat']].append(new_item)
			# yield item







