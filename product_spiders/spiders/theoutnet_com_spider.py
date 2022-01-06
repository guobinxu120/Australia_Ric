# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests, json
from collections import OrderedDict
from scrapy.http import TextResponse


class theoutnet_com_au_Spider(scrapy.Spider):

	name = "theoutnet_com_spider"

	total_count = 0
	result_data_list = {}
	headers = ['PageUrl', 'ProductCategory', 'ProductLink', 'ProductTitle', 'Brand', 'ProductId', 'Quantity', 'ImageLink1', 'ImageLink2', 'ImageLink3', 'ImageLink4', 'DiscountedPrice', 'ProductPrice', 'Color',
			   'Size1', 'Size2', 'Size3', 'Size4', 'Size5', 'Size6', 'Size7', 'Size8', 'Size9', 'Size10', 'Size11', 'Size12', 'DetailFit']
###########################################################

	def __init__(self, *args, **kwargs):
		super(theoutnet_com_au_Spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		filename = "basic_data/categories_theoutnet.txt"
		with open(filename, 'U') as f:
			for category_url in f.readlines():
				cat_name = category_url.strip().split('/')[-1]
				self.result_data_list[cat_name] = []

				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parseProductList, meta={'cat': cat_name})

		########--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.theoutnet.com/en-au/shop/just-in',
		# 			callback=self.parseProductList)
		#################################################

	def parseProductList(self, response):
		products_list = response.xpath('//ul[@class="sr-product-list"]/li')
		for product in products_list:
			json_str = product.xpath('./@data-ytos-track-product-data').extract_first()
			json_data = json.loads(json_str)

			productPrice = json_data['product_price']
			if productPrice == 0:
				productPrice = ''
			meta_data = {'cat': response.meta['cat'],
						 'PageUrl': response.url,
						 'ProductTitle': json_data['product_title'],
						 'Brand': json_data['product_brand'],
						 'ProductId': json_data['product_id'],
						 'Quantity': json_data['product_quantity'],
						 'Color': json_data['product_color'],
						 'ProductCategory': '{}/{}'.format(json_data['product_macro_category'], json_data['product_micro_category']),
						 'ProductPrice': 'AUD {}'.format(productPrice),
						 'DiscountedPrice': 'AUD {}'.format(json_data['product_discountedPrice'])}

			product_href = product.xpath('.//a[@class="itemLink"]/@href').extract_first()
			yield Request(response.urljoin(product_href), callback=self.parseProduct, meta=meta_data)


		next_href = response.xpath('//link[@rel="next"]/@href').extract_first()
		if next_href:
			yield Request(response.urljoin(next_href), callback=self.parseProductList, meta=response.meta)

		########--------- For test -----------###########
		# yield Request(response.urljoin('https://www.theoutnet.com/en-au/shop/product/midi_cod1874378722888941.html#dept=INTL_Just_In'), callback=self.parseProduct)
		#################################################

	def parseProduct(self, response):
		product = response


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''
		item['PageUrl'] = response.meta['PageUrl']
		item['ProductCategory'] = response.meta['ProductCategory']
		item['ProductLink'] = response.url
		item['ProductTitle'] = response.meta['ProductTitle']
		item['Brand'] = response.meta['Brand']
		item['ProductId'] = response.meta['ProductId']
		item['Quantity'] = response.meta['Quantity']
		item['DiscountedPrice'] = response.meta['DiscountedPrice']
		item['ProductPrice'] = response.meta['ProductPrice']
		item['Color'] = response.meta['Color']
		item['DetailFit'] = response.xpath('//*[@class="accordion__content"]/ul').extract_first()


		HTMLListSizeSelector = response.xpath('//*[@class="HTMLListSizeSelector"]/ul/li')
		if HTMLListSizeSelector:
			no_size = False
			n = 1
			for i, size_xpath in enumerate(HTMLListSizeSelector):
				if i > 11:
					break
				if size_xpath.xpath('./@class').extract_first() == 'is-disabled is-soldOut':
					continue


				size_sel = size_xpath.xpath('./@data-ytos-size-model').extract_first()
				size_json = json.loads(size_sel)
				label = size_json['Label']

				if i == 0 and label == '--':
					no_size = True
					break

				name = size_xpath.xpath('./span[@class="sizeActiveSchema"]/text()').extract_first()
				label = size_xpath.xpath('./span[@class="sizeLabel"]/text()').extract_first()
				if not name:
					name = ''
				if name:
					item['Size{}'.format(n + 1)] = '{} {}'.format(name, label)
				else:
					item['Size{}'.format(n + 1)] = str(label)
				n += 1
			if no_size:
				if response.xpath('//*[contains(@class,"addProductToShoppingBagButton")]'):
					item['Size1'] = 'ADD TO BAG'
				else:
					item['Size1'] = 'SOLD OUT'
		else:
			if response.xpath('//*[contains(@class,"addProductToShoppingBagButton")]'):
				item['Size1'] = 'ADD TO BAG'
			else:
				item['Size1'] = 'SOLD OUT'

		image_hrefs = response.xpath('//*[@class="slider slider--main slider--with-thumbs-nav"]//img/@src').extract()
		if image_hrefs:
			for j, img_src in enumerate(image_hrefs):
				if j > 3:
					break
				item['ImageLink{}'.format(j + 1)] = img_src

		self.total_count += 1
		# print 'total_count: ' + str(self.total_count)
		# print item
		self.result_data_list[response.meta['cat']].append(item)
		# yield item







