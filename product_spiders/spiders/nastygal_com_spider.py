# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
import requests
from collections import OrderedDict
from scrapy.http import TextResponse


class nastygal_com_au_Spider(scrapy.Spider):

	name = "nastygal_com_spider"

	total_count = 0
	result_data_list = {}
	headers = ['ProductLink', 'ProductTitle', 'Category1', 'Category2', 'Category3', 'StyleNumber', 'Image_1', 'Image_2', 'Image_3', 'Image_4', 'StandardPrice', 'SalePrice', 'Description', 'Color',
			   'Size_L', 'Size_XL', 'Size_M/L', 'Size_S', 'Size_XS', 'Size_S/M', 'Size_M', 'Size_ONE_SIZE',
			   'Size_3', 'Size_4', 'Size_5', 'Size_6', 'Size_7', 'Size_8', 'Size_9', 'Size_10', 'Size_11', 'Size_12', 'Size_13', 'Size_14', 'Size_15', 'Size_16']


###########################################################

	def __init__(self, *args, **kwargs):
		super(nastygal_com_au_Spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		filename = "basic_data/categories_nastygal.txt"
		with open(filename, 'U') as f:
			for category_url in f.readlines():
				cat_name = category_url.strip().split('/')[-1]
				self.result_data_list[cat_name] = []
				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parseProductList, meta={'cat': cat_name})

		########--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.nastygal.com/au/womens',
		# 			callback=self.parseProductList)
		#################################################

	def parseProductList(self, response):
		products_list = response.xpath('//ul[@id="search-result-items"]/li//a[@class="thumb-link"]/@href').extract()
		for product_href in products_list:
			yield Request(response.urljoin(product_href.replace('/gb/', '/au/')), callback=self.parseProduct, meta=response.meta)


		next_href = response.xpath('//*[@title="Next"]/@href').extract_first()
		if next_href:
			yield Request(response.urljoin(next_href), callback=self.parseProductList, meta=response.meta)

		########--------- For test -----------###########
		# yield Request(response.urljoin('https://www.nastygal.com/au/dont-sugercoat-it-longline-coat/AGG92914-1.html'), callback=self.parseProduct)
		#################################################

	def parseProduct(self, response):
		product = response


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['ProductLink'] = response.url
		item['StyleNumber'] = response.xpath('//span[@itemprop="sku"]/text()').re_first(r'^([^-]+)')
		item['ProductTitle'] = product.xpath('.//h1[@itemprop="name"]/text()').extract_first().encode('utf-8')
		item['SalePrice'] = product.xpath('.//span[@itemprop="price"]/@content').extract_first()

		cats = product.xpath('//*[@class="breadcrumb-element"]/text()').extract()
		if cats:
			cats.pop()
		if 'Home' in cats:
			cats.remove('Home')

		for i, cat in enumerate(cats):
			if i > 2:
				break
			item['Category{}'.format(str(i + 1))] = cat.encode('utf-8')

		product_description = product.xpath('.//*[@class="product-description"]//text()').extract()
		if product_description:
			new_d = []
			for d in product_description:
				d = d.encode('utf-8').strip()
				if d:
					new_d.append(d)
			item['Description'] = '\n'.join(new_d)

		standard_price = response.xpath('//span[@class="price-standard"]/text()').re_first(r'\$(.+)')
		if standard_price:
			item['StandardPrice'] = standard_price

		item['Image_1'] = response.urljoin(product.xpath('.//meta[@property="og:image"]/@content').extract_first().split('?')[0])

		image_id = item['Image_1'].split('/')[-1]
		for i in range(3):
			image_id_temp = image_id + '_{}'.format(i + 1)
			item['Image_{}'.format(i + 2)] = item['Image_1'].replace(image_id, image_id_temp)

		if product.xpath('//ul[@class="swatches color"]/li//img/@alt').extract_first():
			if product.xpath('//ul[@class="swatches color"]/li[contains(@class,"selectable selected")]//img/@alt').extract_first():
				item['Color'] = product.xpath('//ul[@class="swatches color"]/li[contains(@class,"selectable selected")]//img/@alt').extract_first().replace('\n', '')
			else:
				item['Color'] = product.xpath('//ul[@class="swatches color"]/li//img/@alt').extract_first().replace('\n', '')

			color_xpaths = product.xpath('//ul[@class="swatches color"]/li[contains(@class,"selectable selected")]')

			temp_size_hrefs = product.xpath('//ul[@class="swatches size"]/li/span')
			temp_size_hrefs_selected = product.xpath('//ul[@class="swatches size"]/li[contains(@class,"selectable selected")]')
			if not temp_size_hrefs_selected:
				if not color_xpaths:
					if product.xpath('//ul[@class="swatches color"]/li'):
						color_xpath = product.xpath('//ul[@class="swatches color"]/li')[0]
					# for color_xpath in color_xpaths:
						href_list = color_xpath.xpath('./span/@data-href').extract_first().split('&')
						basic = href_list[0] + '&'
						color_id = href_list[1]
						vgid = href_list[2]

						size_hrefs = product.xpath('//ul[@class="swatches size"]/li/span')
						for i, size_xpath in enumerate(size_hrefs):
							if not size_xpath.xpath('./@data-href').extract_first():
								continue
							size_id = size_xpath.xpath('./@data-href').extract_first().split('&')[1]
							href = basic + color_id + '&' + size_id + '&' + vgid + '&' + '&Quantity=1&format=ajax&productlistid=undefined'
							# href = size_xpath.xpath('./@data-href').extract_first() + '&Quantity=1&format=ajax&productlistid=undefined'
							r = requests.get(href).text

							resp1 = TextResponse(url='',
												body=r,
												encoding='utf-8')
							qty = ''.join(resp1.xpath('//*[@class="in-stock-msg"]/text()').re(r'[\d.,]+'))

							if qty:
								qty = qty.strip()
							else:
								qty = ''

							size_str = size_xpath.xpath('./text()').extract_first()
							if size_str:
								size_str = size_str.strip()
								if size_str.upper() == 'ONE SIZE':
									size_str = 'ONE_SIZE'


							size_str = 'Size_' + size_str

							if size_str not in self.headers:
								self.headers.append(size_str)


							qty_str = ''.join(resp1.xpath('//*[@class="in-stock-msg"]/text()').extract())
							if qty_str:
								if 'stock' in qty_str.lower():
									qty = qty_str.strip()

							item[size_str] = qty

				else:
					size_hrefs = product.xpath('//ul[@class="swatches size"]/li/span')
					for i, size_xpath in enumerate(size_hrefs):
						if not size_xpath.xpath('./@data-href').extract_first():
							continue
						href = size_xpath.xpath('./@data-href').extract_first() + '&Quantity=1&format=ajax&productlistid=undefined'
						r = requests.get(href).text

						resp1 = TextResponse(url='',
											body=r,
											encoding='utf-8')
						qty = ''.join(resp1.xpath('//*[@class="in-stock-msg"]/text()').re(r'[\d.,]+'))
						if qty:
							qty = qty.strip()

						size_str = size_xpath.xpath('./text()').extract_first()
						if size_str:
							size_str = size_str.strip()
							if size_str.upper() == 'ONE SIZE':
								size_str = 'ONE_SIZE'

						size_str = 'Size_' + size_str

						if size_str not in self.headers:
							self.headers.append(size_str)

						qty_str = ''.join(resp1.xpath('//*[@class="in-stock-msg"]/text()').extract())
						if qty_str:
							if 'stock' in qty_str.lower():
								qty = qty_str.strip()

						item[size_str] = qty
			else:
				# print 'One SIZE'
				qty = ''.join(response.xpath('//*[@class="in-stock-msg"]/text()').re(r'[\d.,]+'))
				if qty:
					qty = qty.strip()

				size_xpath = temp_size_hrefs_selected[0]
				size_str = size_xpath.xpath('./span/text()').extract_first()
				if size_str:
					size_str = size_str.strip()
					if size_str.upper() == 'ONE SIZE':
						size_str = 'ONE_SIZE'


				size_str = 'Size_' + size_str

				if size_str not in self.headers:
					self.headers.append(size_str)

				qty_str = ''.join(response.xpath('//*[@class="in-stock-msg"]/text()').extract())
				if qty_str:
					if 'stock' in qty_str.lower():
						qty = qty_str.strip()

				item[size_str] = qty


				# for color_xpath in color_xpaths:
				# 	href = color_xpath.xpath('./span/@data-href').extract_first() + '&Quantity=1&format=ajax&productlistid=undefined'
				# 	r = requests.get(href).text
                #
				# 	resp1 = TextResponse(url='',
				# 						body=r,
				# 						encoding='utf-8')
				# 	qty = ''.join(resp1.xpath('//*[@class="in-stock-msg"]/text()').re(r'[\d.,]+'))
				# 	if qty:
				# 		qty = qty.strip()
                #
				# 	size_str = 'qty'
                #
				# 	if size_str not in self.headers:
				# 		self.headers.append(size_str)
                #
				# 	qty_str = ''.join(resp1.xpath('//*[@class="in-stock-msg"]/text()').extract())
				# 	if qty_str:
				# 		if 'stock' in qty_str.lower():
				# 			qty = qty_str.strip()
                #
				# 	item[size_str] = qty

		self.total_count += 1
		# print 'total_count: ' + str(self.total_count)
		# print item
		self.result_data_list[response.meta['cat']].append(item)
		# yield item







