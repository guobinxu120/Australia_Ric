# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "harrisre_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'harrisre_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'mobile', 'direct number', 'facebook', 'instagram', 'twitter', 'linkedin', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='http://www.harrisre.com.au/department/sales/',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="row equal bottom-20"]/div[@class="col-sm-3"]/div')

			if not products_list:
				return
			for pro in products_list:

				url = pro.xpath('./a/@href').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					# name = pro.xpath('./div/div[@class="details"]/h2/text()').extract_first()
					# agent_role = pro.xpath('./div/div[@class="details"]/h3/text()').extract_first()
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True)
				else:
					item = OrderedDict()

					for h in self.headers:
						item[h] = ''

					name = pro.xpath('./div[@class="team-card-content"]/div[@class="team-card-author-title up-10"]/text()').extract_first()
					if name:
						name = name.strip()
					item['name'] = name
					agent_role = pro.xpath('./div[@class="team-card-content"]/div[@class="team-card-author-position"]/text()').extract_first()
					item['agent role'] = agent_role
					email = pro.xpath('./div[@class="team-card-content"]/div[@class="team-card-author-email"]/text()').extract_first()
					if email:
						email = email.strip()
					item['email'] = email
					phone = pro.xpath('./div[@class="team-card-content"]/div[@class="team-card-author-mobile"]/text()').extract_first()
					if phone:
						phone = phone.strip()
						if 'M:' in phone:
							item['mobile'] = phone.replace('M:', '')
						elif 'P:' in phone:
							item['direct number'] = phone.replace('P:', '')

					self.total_count += 1
					print('total_count: ' + str(self.total_count))
					print item
					self.result_data_list[str(self.total_count)] = item



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



		item['name'] = response.xpath('//div[@class="single-directory-title"]/h1/text()').extract_first()
		item['agent role'] = response.xpath('//div[@class="single-directory-title"]/h2/text()').extract_first()

		if 'M:' in response.xpath('//div[@class="single-directory-contact-phone"]/text()').extract_first():
			item['mobile'] = response.xpath('//div[@class="single-directory-contact-phone"]/a/text()').extract_first()
		elif 'P:' in response.xpath('//div[@class="single-directory-contact-phone"]/text()').extract_first():
			item['direct number'] = response.xpath('//div[@class="single-directory-contact-phone"]/a/text()').extract_first()

		item['email'] = response.xpath('//div[@class="single-directory-contact-email"]/a/text()').extract_first()


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
		socials = response.xpath('//div[@class="single-directory-social-media-icons"]/table/tr/td/a/@href').extract()
		for label in socials:
			if 'facebook.com' in label:
				item['facebook'] = label
			elif 'twitter.com' in label:
				item['twitter'] = label
			elif 'instagram.com' in label:
				item['instagram'] = label
			elif 'linkedin.com' in label:
				item['linkedin'] = label

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[contains(@id,"about")]/div/div/div/p/text()').extract()
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








