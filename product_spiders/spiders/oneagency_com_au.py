# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "oneagency_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'oneagency_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'mobile', 'office name', 'office phone number', 'office website', 'Office Address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://oneagency.com.au/agents?order=name&type=Agent&name=&property_type=&property_category=&price_from=&price_to=&beds=&state=&region=&suburb=',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//a[@class="agent-link image-hover"]')

			if not products_list:
				return
			for pro in products_list:
				url = pro.xpath('./@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					# name = pro.xpath('./div/div[@class="details"]/h2/text()').extract_first()
					# agent_role = pro.xpath('./div/div[@class="details"]/h3/text()').extract_first()
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True)
				# break
		except:

			i = 1
			i +=1

		page_num = response.meta['page_num'] + 1
		yield scrapy.Request(
			url='https://oneagency.com.au/ajax-agents?limit=20&name=&state=&region=&suburb=&order=name&order=&order=name&&type=Agent&&name=&&property_type=&&property_category=&&price_from=&&price_to=&&beds=&&state=&&region=&&suburb=&&offset={}'.format(str(page_num * 20)),
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''



		item['name'] = response.xpath('//meta[@property="og:title"]/@content').extract_first()

		item['mobile'] = response.xpath('//div[@id="consultant-agent-personal"]/div[@class="agent-details-info-number"]/div/a/text()').extract_first()
		item['email'] = response.xpath('//div[@id="consultant-agent-personal"]/div[@class="agent-details-info-number"]/div/a/@title').extract_first()

		item['office name'] = response.xpath('//div[@id="consultant-agent-office"]/div[@class="agent-details-info-name"]/strong/a/text()').extract_first()
		item['office phone number'] = response.xpath('//div[@id="consultant-agent-office"]/div[@class="agent-details-info-number"]/div/a[contains(@href,"tel:")]/text()').extract_first()
		website = response.xpath('//div[@id="consultant-agent-office"]/div[@class="agent-details-info-number"]/div/a[@target="_blank"]/text()').extract_first()
		if website:
			item['office website'] = website.strip()
		item['Office Address'] = response.xpath('//div[@id="consultant-agent-location"]/div[@class="agent-details-info-number"]/div/text()').extract_first()
		# for d in consultant_agent_office:
		# 	if d:
		# 		d = d.strip()
		# 	if d:
		# 		if '@':
		# 			item['email'] = d
		# 		else:


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
		# socials = response.xpath('//p[@class="agent-social"]/a/@href').extract()
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




		profiles = response.xpath('//div[@id="consultant-agent-information"]/p/text()').extract()
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








