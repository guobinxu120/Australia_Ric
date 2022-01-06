# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "hodges_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'hodges_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'mobile', 'direct number', 'facebook', 'twitter','linkedin', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.hodges.com.au/real-estate-agents/page/1/?office&position&agent&order&ajax=1',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="tablet-only medium-6 large-3 columns end"]')

			if not products_list:
				return
			for pro in products_list:
				url = pro.xpath('.//a/@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					name = pro.xpath('./div/div[@class="details"]/h2/text()').extract_first()
					agent_role = pro.xpath('./div/div[@class="details"]/h3/text()').extract_first()
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True,
						meta={
							'name':name,
							'agent_role':agent_role
						})
				# break
		except:

			i = 1
			i +=1

		page_num = response.meta['page_num'] + 1
		yield scrapy.Request(
			url='https://www.hodges.com.au/real-estate-agents/page/{}/?office&position&agent&order&ajax=1'.format(str(page_num)),
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.meta['name']
		# agent_role = response.meta['agent_role']
		# item['agent role'] = agent_role

		item['agent role'] = response.xpath('//p[@class="agent-position"]/text()').extract_first()

		# phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		# item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		socials = response.xpath('//div[@class="agent-contact"]/p[@class="agent-phone"]')
		for so in socials:
			label = so.xpath('./span/text()').extract_first()
			if not label:
				continue
			if 'Direct' in label:
				item['direct number'] = so.xpath('./span/a/text()').extract_first()
			elif 'Mobile' in label:
				item['mobile'] = so.xpath('./span/a/text()').extract_first()
			# elif 'Fax' in label:
			# 	item['fax'] = so.xpath('./td/div[@itemprop="faxNumber"]/text()').extract_first()

		email = response.xpath('//p[@class="agent-email"]/a/text()').extract_first()
		if email:
			item['email'] = email.replace('mailto:', '')

		socials = response.xpath('//p[@class="agent-social"]/a/@href').extract()
		for label in socials:
			if 'facebook.com' in label:
				item['facebook'] = label
			elif 'twitter.com' in label:
				item['twitter'] = label
			elif 'linkedin.com' in label:
				item['linkedin'] = label

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="read-more"]/p/text()').extract()
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








