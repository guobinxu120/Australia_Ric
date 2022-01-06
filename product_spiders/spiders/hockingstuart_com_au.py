# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "hockingstuart_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'hockingstuart_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'mobile', 'facebook', 'linkedin', 'twitter', 'office_name', 'office_phone','office_email', 'office_address', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		f2 = open('basic_data/hockingstuart_office_urls.csv')

		csv_items = csv.DictReader(f2)
		cat_data = {}

		for i, row in enumerate(csv_items):
			v = row['url']
			yield scrapy.Request(
				url='https://www.hockingstuart.com.au' + v,
				callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})
			# break
		f2.close()

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="col-xs-12 col-sm-6 col-md-6 col-lg-4 flex_col--top text_center mb4"]/div')

			if not products_list:
				return

			office_name = response.xpath('//p[@class="font_gilroysemibold mb0 address_title"]/text()').extract_first()
			office_address = response.xpath('//p[@class="mb2 address"]/text()').extract_first()
			office_datas = response.xpath('//p[@class="mb2 address"]//text()').extract()
			office_phone = ''
			office_email = ''
			for of in office_datas:
				if 'Tel ' in of:
					office_phone = of.replace('Tel ', '')
				elif '@' in of:
					office_email = of
			for pro in products_list:
				url = pro.xpath('./div/a/@href').extract_first()
				name = pro.xpath('./p[@class="team_profiles__name font_gilroysemibold h5"]/text()').extract_first()
				if name:
					name = name.strip()
				agent_role = pro.xpath('./p[@class="mb0"]/text()').extract_first()
				if agent_role:
					agent_role = agent_role.strip()


				if url:
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
						url=url,
						callback=self.parseProduct, dont_filter=True,
						meta={
							'name':name,
							'agent_role': agent_role,
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
		item['office_name'] = response.meta['office_name']
		item['office_address'] = response.meta['office_address']
		item['office_phone'] = response.meta['office_phone']
		item['office_email'] = response.meta['office_email']

		data = response.xpath('//div[@class="agent-content background_light_grey"]/div[@class="text__block"]/p/a/@href').extract()
		for d in data:
			if 'tel:' in d:
				item['mobile'] = d.replace('tel:', '')
			elif '@':
				item['email'] = d.replace('mailto:', '')


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
		socials = response.xpath('//ul[@class="text__block--social social_icons mb2"]/li/a/@href').extract()
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




		profiles = response.xpath('//div[@class="hidden-sm-down"]/div[@class="text__block"]/p/text()').extract()
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








