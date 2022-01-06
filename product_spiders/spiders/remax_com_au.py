# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "remax_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'remax_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'mobile', 'direct number', 'website', 'address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		form_data = {'page': '1','Suburbs_id':'' }
		yield scrapy.FormRequest(
			url='https://www.remax.com.au/ajax/search_staff_member.php', formdata=form_data,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parse1(self, response):
		products_list = response.xpath('//table/tr[@class="searchResults"]')
		url_list = []
		for product in products_list:
			url = product.xpath('./td/a/@href').extract_first()
			if not url or (url in url_list):
				continue
			url_list.append(url)

			name = product.xpath('./td/a/text()').extract_first()

			location = product.xpath('./td[2]/text()').extract_first()
			if location:
				location = location.strip().replace('\n', '').replace('\t', '').replace('\r', ' ')

			yield scrapy.Request(
				url=response.urljoin(url),
				callback=self.parseProduct, dont_filter=True, meta={'name': name,
																		'location': location})
			# break

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="col-xs-12 col-sm-6 col-md-3 box-pad-righ agent-img-four"]/div/a')

			if not products_list:
				return
			for pro in products_list:
				# name = pro.xpath('.//div[@class="address"]/a/h3/text()').extract_first()
				url = pro.xpath('./@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True)
				# break
		except:

			i = 1
			i +=1

		page_num = response.meta['page_num'] + 1
		form_data = {'page': str(page_num),'Suburbs_id':'' }
		yield scrapy.FormRequest(
			url='https://www.remax.com.au/ajax/search_staff_member.php', formdata=form_data,
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//p[@class="c-card__text mb5 bold-tex fnt-16 mt5"]/text()').extract_first()
		item['agent role'] = response.xpath('//p[@class="agent-list__text mb5"]/text()').extract_first()

		datas = []
		datas = response.xpath('//div[@class="c-card__item-agt-body  tex-cent"]/p/a/text()').extract()
		for d in datas:
			if '@' in d:
				item['email'] = d
				datas.remove(d)
		if len(datas) > 1:
			item['mobile'] = datas[0]
			item['direct number'] = datas[1]
		elif len(datas) == 1:
			item['mobile'] = datas[0]

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

		profiles = response.xpath('//div[@class="go-b-re mb10 mt20"]/span/text()').extract()
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








