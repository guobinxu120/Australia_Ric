# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "independent_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'independent_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'mobile', 'direct number', 'website', 'twitter', 'linkedin', 'facebook', 'instagram', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://independent.com.au/real-estate-agents-near-me',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@role="tabpanel"]/div/div[@class="team-member"]')

			if not products_list:
				return
			for pro in products_list:
				# name = pro.xpath('.//div[@class="address"]/a/h3/text()').extract_first()
				url = pro.xpath('./div/a/@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					name = pro.xpath('./div/div[@class="team-title"]/a/text()').extract_first()
					agent_role = pro.xpath('./div/div[@class="team-role"]/text()').extract_first()
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True,
						meta={
							'name':name,
							'agent_role':agent_role
						})
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

		item['name'] = response.meta['name']
		role = response.meta['agent_role']
		item['agent role'] = role

		phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		if phone:
			phone = phone.strip()
		item['direct number'] = phone
		item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		socials = response.xpath('//ul[@class="soxial small"]/li/a/@href').extract()
		for so in socials:
			if 'facebook.com' in so:
				item['facebook'] = so
			elif 'instagram.com' in so:
				item['instagram'] = so
			elif 'twitter.com' in so:
				item['twitter'] = so
			elif 'linkedin.com' in so:
				item['linkedin'] = so

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="agent-info"]/p/text()').extract()
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








