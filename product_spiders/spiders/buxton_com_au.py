# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "buxton_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'buxton_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'mobile', 'office_name', 'office_phone','office_email', 'office_address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://buxton.com.au/our-offices/',
			callback=self.parseOffices, dont_filter=True, meta={'page_num': 1})

	def parseOffices(self, response):
		offices_list = response.xpath('//div[@class="columns small-12 medium-6 large-4"]/a/@href').extract()
		for o in offices_list:
			yield scrapy.Request(
				url=response.urljoin(o),
				callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})
			# break

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="columns small-6 medium-4 large-3"]/a')

			if not products_list:
				return

			office_name = response.xpath('//h2[@class="office-name"]/text()').extract_first()
			office_address = response.xpath('//div[@class="office-address"]/text()').extract_first()
			office_phone = response.xpath('//div[@class="office-phone"]/text()').extract_first()
			if office_phone:
				office_phone = office_phone.replace('Telephone ', '')
			office_email = response.xpath('//div[@class="office-email"]/a/@href').extract_first()

			for pro in products_list:
				url = pro.xpath('./@href').extract_first()
				name = pro.xpath('./div/div[@class="agent-details"]/h3[@class="agent-name"]/text()').extract_first()
				if name:
					name = name.strip()
				agent_role = pro.xpath('./div/div[@class="agent-details"]/div[@class="agent-position"]/text()').extract_first()
				agent_phone = pro.xpath('./div/div[@class="agent-details"]/div[@class="agent-phone"]/text()').extract_first()
				if agent_phone:
					agent_phone = agent_phone.replace('Mobile: ', '')

				if url:
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
						url=url,
						callback=self.parseProduct, dont_filter=True,
						meta={
							'name':name,
							'agent_role': agent_role,
							'agent_phone': agent_phone,
							'office_name': office_name,
							'office_address': office_address,
							'office_phone': office_phone,
							'office_email': office_email
						}
					)
				# break
		except:

			i = 1
			i +=1

		# page_num = response.meta['page_num'] + 1
		# yield scrapy.Request(
		# 	url='https://oneagency.com.au/ajax-agents?limit=20&name=&state=&region=&suburb=&order=name&order=&order=name&&type=Agent&&name=&&property_type=&&property_category=&&price_from=&&price_to=&&beds=&&state=&&region=&&suburb=&&offset={}'.format(str(page_num * 20)),
		# 	callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):
		item = OrderedDict()
		for h in self.headers:
			item[h] = ''

		item['name'] = response.meta['name']
		item['agent role'] = response.meta['agent_role']
		item['mobile'] = response.meta['agent_phone']
		item['office_name'] = response.meta['office_name']
		item['office_address'] = response.meta['office_address']
		item['office_phone'] = response.meta['office_phone']
		item['office_email'] = response.meta['office_email']

		item['email'] = response.xpath('//div[@class="agent-email"]/text()').extract_first()
		if item['email']:
			item['email'] = item['email'].replace('Email: ', '')
		# agent_role = response.meta['agent_role']
		# item['agent role'] = agent_role

		# item['agent role'] = response.xpath('//p[@class="agent-position"]/text()').extract_first()

		# phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		# item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		# socials = response.xpath('//div[@class="consultant-agent-information"]/p[@class="agent-phone"]')
		# for so in socials:
		# 	label = so.xpath('./span/text()').extract_first()
		# 	if not label:
		# 		continue
		# 	if 'Direct' in label:
		# 		item['direct number'] = so.xpath('./span/a/text()').extract_first()
		# 	elif 'Mobile' in label:
		# 		item['mobile'] = so.xpath('./span/a/text()').extract_first()
		# 	# elif 'Fax' in label:
		# 	# 	item['fax'] = so.xpath('./td/div[@itemprop="faxNumber"]/text()').extract_first()
        #
		# email = response.xpath('//p[@class="agent-email"]/a/text()').extract_first()
		# if email:
		# 	item['email'] = email.replace('mailto:', '')
        #
		# socials = response.xpath('//ul[@class="text__block--social social_icons mb2"]/li/a/@href').extract()
		# for label in socials:
		# 	if 'facebook.com' in label:
		# 		item['facebook'] = label
		# 	elif 'twitter.com' in label:
		# 		item['twitter'] = label
		# 	elif 'linkedin.com' in label:
		# 		item['linkedin'] = label

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="agent-description"]/p/text()').extract()
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








