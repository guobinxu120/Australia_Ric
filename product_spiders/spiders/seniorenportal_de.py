# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class seniorenportal_de_spider(scrapy.Spider):

	name = "seniorenportal_de"

	total_count = 0
	use_selenium = True
	result_data_list = []
	filepath = 'seniorenportal_de.xlsx'
	headers = ['company name', 'Company Address', 'Phone', 'website', 'url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(seniorenportal_de_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		url = 'https://www.guntrader.uk/dealers'
		yield scrapy.Request(
			url=url,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parse_state(self, response):
		urls = response.xpath('//div[@class="custom-multi-list-group clearfix style-1"]/div/a')
		for url_tag in urls:
			url = url_tag.xpath('./@href').extract_first()
			state = url_tag.xpath('./text()').extract_first().replace('Apotheken in ', '')
			yield scrapy.Request(
				url=response.urljoin(url),
				callback=self.parse_city, dont_filter=True, meta={'state': state})
			break

	def parse_city(self, response):
		urls_tages = response.xpath('//div[@class="list-group"]/a')
		for i, url_tag in enumerate(urls_tages):
			url = url_tag.xpath('./@href').extract_first()
			city = url_tag.xpath('./strong/text()').extract_first()
			response.meta['city'] = city
			yield scrapy.Request(
				url=response.urljoin(url),
				callback=self.parseProductList, dont_filter=True, meta=response.meta)

			# break
			if i == 20:
				break

	def parseProductList(self, response):
		# state = response.meta['state']
		# city = response.meta['city']

		products_list = response.xpath('//ul[@class="dealerList"]/li')

		if not products_list:
			return
		for product in products_list:
			company_name = product.xpath('./h2/text()').extract_first()

			addresses = product.xpath('.//p[@class="address"]//text()').extract()

			Address = '\n'.join(addresses).strip()
			Phone = product.xpath('.//p[@class="phone"]/label/span/text()').extract_first()
			website = product.xpath('.//p[@class="website"]/a/@href').extract_first()
			url = response.urljoin(product.xpath('.//p[@class="guns"]/a/@href').extract_first())
			# if url in self.result_data_list:
			# 	return
			self.result_data_list.append(url)

			item = OrderedDict()

			item['company name'] = company_name
			item['Company Address'] = Address
			item['Phone'] = Phone
			item['website'] = website
			item['url'] = url

			self.total_count += 1
			print('total_count: ' + str(self.total_count))
			print item
			# self.result_data_list[str(self.total_count)] = item
			yield item



			# break
		if response.meta['page_num'] == 12:
			return
		response.meta['page_num'] += 1
		next_url = 'https://www.guntrader.uk/dealers?page=' + str(response.meta['page_num'])
		yield scrapy.Request(
			url=next_url,
			callback=self.parseProductList, dont_filter=True, meta=response.meta)
		# response.meta['page_num'] += 1
		# next_url = response.xpath('//span[@class="pmpro_next"]/a/@href').extract_first()
		# if next_url:
		# 	yield scrapy.Request(
		# 		url=next_url,
		# 		callback=self.parseProductList, dont_filter=True, meta=response.meta)