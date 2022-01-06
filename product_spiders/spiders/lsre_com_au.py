# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "lsre_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'lsre_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'mobile', 'direct number1', 'direct number2', 'website', 'address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		form_data = {'page': '1','Suburbs_id':'' }
		yield scrapy.Request(
			url='https://lsre.com.au/wp-json/listings/v1/agents?key=94d5152c838ec2e4ec9c0128f6e6ec53&type=&agent-name=&page=1',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = loads(response.body)

			if not products_list:
				return
			for pro in products_list:
				name = pro['name']
				position = ', '.join(pro['position'])
				url = pro['agent_url']
				if url:
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True, meta={'name': name,
																				'position': position})
				# break
		except:

			i = 1
			i +=1

		page_num = response.meta['page_num'] + 1
		yield scrapy.Request(
			url='https://lsre.com.au/wp-json/listings/v1/agents?key=94d5152c838ec2e4ec9c0128f6e6ec53&type=&agent-name=&page={}'.format(page_num),
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.meta['name']
		item['agent role'] = response.meta['position']

		item['company'] = response.xpath('//div[@class="author-office-item"]/a/text()').extract_first()

		datas = []
		item['email'] = response.xpath('//div[@class="author-email"]/a/text()').extract_first()
		datas = response.xpath('//div[@class="author-tel"]')
		for d in datas:
			name = d.xpath('./b/text()').extract_first()
			val = d.xpath('./a/text()').extract_first()
			if name == 'M':
				item['mobile'] = val
			elif name == 'T':
				if not item['direct number1']:
					item['direct number1'] = val
				else:
					item['direct number2'] = val

			# name = d.xpath('./th/text()').extract_first()
			# if name == 'Address:':
			# 	values = d.xpath('./td/text()').extract()
			# 	val_list = []
			# 	for v in values:
			# 		if v:
			# 			v = v.strip().replace('\n', '').replace('\t', '').replace('\r', ' ')
			# 			if v:
			# 				val_list.append(v)
			# 	val = ''
			# 	if val_list:
			# 		val = '\n'.join(val_list)
			# 	item['address'] = val
			# elif name == 'Phone:':
			# 	value = d.xpath('./td/text()').extract_first()
			# 	item['phone'] = value
			# elif name == 'Email:':
			# 	value = d.xpath('./td/a/text()').extract_first()
			# 	item['email'] = value
			# elif name == 'Web:':
			# 	value = d.xpath('./td/a/@href').extract_first()
			# 	item['website'] = value
			# elif name == 'Fax:':
			# 	value = d.xpath('./td/text()').extract_first()
			# 	item['fax'] = value

		profiles = response.xpath('//div[@class="col span_12 author-bio center-container"]/p/text()').extract()
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








