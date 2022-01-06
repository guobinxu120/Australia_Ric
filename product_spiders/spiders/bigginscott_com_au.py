# -*- coding: utf-8 -*-
import scrapy, csv
from scrapy import Request
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "bigginscott_com_au"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'bigginscott_com_au_sel22.xlsx'
	headers = ['name', 'office', 'agent role', 'email', 'mobile', 'phone', 'website', 'detail url']
###########################################################

	got_urls = []

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################
	def start_requests(self):
		f2 = open('missing_urls.csv')

		csv_items = csv.DictReader(f2)
		cat_data = {}

		for i, row in enumerate(csv_items):
			# v = row['url'].split('/')[-1]
			yield scrapy.Request(url=row['url'], callback=self.parseItem, dont_filter=True, meta={'url':row['url']})
		f2.close()


	# def start_requests(self):
	# 		url = 'https://www.bigginscott.com.au/about/our-team'
    #
	# 		yield scrapy.Request(
	# 			url=url,
	# 			callback=self.parseProductList, dont_filter=True, meta={'url':url, 'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//section[@class="page-container"]//ul[@class="agents listings-grid"]/li/a/@href').extract()

			if not products_list:
				return
			for pro in products_list:
				if '=undefined' in pro:
					continue
				yield scrapy.Request(url='https://www.bigginscott.com.au' + pro, callback=self.parseItem, dont_filter=True, meta={'url':'https://www.bigginscott.com.au' + pro})
				# break


		except:

			i = 1
			i +=1

			return

		# response.meta['page_num'] = response.meta['page_num'] + 1
		# print('page count: ' + str(response.meta['page_num']))
        #
		# next_url = response.meta['url'] + '&pageIndex=' + str(response.meta['page_num'])
		# if next_url:
		# 	yield scrapy.Request(response.urljoin(next_url), self.parseProductList, dont_filter=True, meta=response.meta)


	def parseItem(self, response):

		if 'missing' in response.url:
			yield {'url': response.meta['url']}
			return


		item = OrderedDict()
		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//header[@class="section-title"]/h2/text()').extract_first()
		item['agent role'] = response.xpath('//header[@class="section-title"]/p/text()').extract_first()

		data = response.xpath('//header[@class="section-title"]/p/a/@href').extract()
		for d in data:
			if 'tel:' in d:
				d = d.replace('tel:', '')
				item['mobile'] = d
			elif 'mailto:' in d:
				d = d.replace('mailto:', '')
				item['email'] = d

		item['detail url'] = response.url

		# item = response.meta['item']
		# role = response.xpath('//div[@class="detailName has-photo"]/h2/text()').extract_first()
		# if role:
		# 	role = role.strip()
		# item['agent role'] = role
        #
		# office = response.xpath('//div[@class="detailOffice"]/a/text()').extract_first()
		# if office:
		# 	office = office.strip()
		# item['office'] = office
        #
		# detailNumbers = response.xpath('//div[@class="detailNumbers"]/div')
		# for num_tag in detailNumbers:
		# 	name = num_tag.xpath('./span/text()').extract()
		# 	if 'Mobile:' in name:
		# 		item['mobile'] = num_tag.xpath('./a/text()').extract_first()
		# 	elif 'Phone:' in name:
		# 		item['phone'] = num_tag.xpath('./a/text()').extract_first()
		# 	elif 'Email:' in name:
		# 		item['email'] = num_tag.xpath('./a/text()').extract_first()
		# 	elif 'Web:' in name:
		# 		item['website'] = num_tag.xpath('./a/text()').extract_first()

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item









