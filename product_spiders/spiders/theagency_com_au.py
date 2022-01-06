# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "theagency_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'theagency_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'mobile', 'direct number', 'fax', 'website', 'facebook', 'instagram', 'streetAddress', 'addressLocality', 'addressRegion', 'postalCode', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		form_data = {'page': '1','Suburbs_id':'' }
		yield scrapy.Request(
			url='https://theagency.com.au/agents',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//ul[@class="teamList grid-1 grid-sml-2 grid-med-4 center"]/li/div/a')

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
				# 	yield scrapy.Request(
				# 			url='https://theagency.com.au/team/steven-chen',
				# 			callback=self.parseProduct, dont_filter=True)
				# break
		except:

			i = 1
			i +=1

		# page_num = response.meta['page_num'] + 1
		# form_data = {'page': str(page_num),'Suburbs_id':'' }
		# yield scrapy.FormRequest(
		# 	url='https://www.remax.com.au/ajax/search_staff_member.php', formdata=form_data,
		# 	callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//span[@itemprop="name"]/text()').extract_first()
		role = response.xpath('//small[@itemprop="jobTitle"]/text()').extract_first()
		if role:
			role = role.strip()
		item['agent role'] = role
		contact_infos = response.xpath('//ul[@class="contact-info"]/li')
		for contact_info in contact_infos:
			title = contact_info.xpath('./abbr/@title').extract_first()
			d = contact_info.xpath('./a/text()').extract_first()
			if title == 'E-mail':
				item['email'] = d
			elif title == 'Mobile':
				item['mobile'] = d
			elif title == 'Telephone':
				item['direct number'] = d
			elif title == 'Fax':
				item['fax'] = d

		socials = response.xpath('//ul[@class="social"]/li/a/@href').extract()
		for so in socials:
			if 'facebook.com' in so:
				item['facebook'] = so
			elif 'instagram.com' in so:
				item['instagram'] = so

		item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="contentRegion "]/p/text()').extract()
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








