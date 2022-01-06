# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "acton_com_au"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'acton_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'mobile', 'direct number', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.acton.com.au/our-team/sales-team',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//div[@class="teamBio col-sm-4 col-xs-12"]')

			if not products_list:
				return
			for pro in products_list:
				onclick = pro.xpath('./@onclick').extract_first()
				url = onclick.split('=')[-1].replace("'", '')
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					# name = pro.xpath('./h4[@id="mlk-11"]/text()').extract_first()
					# company = pro.xpath('./h4[@id="mlk-14"]/text()').extract_first()
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True)
				# break
		except:

			i = 1
			i += 1

		# page_num = response.meta['page_num'] + 1
		# yield scrapy.Request(
		# 	url='https://www.peterblackshaw.com.au/find-an-agent.html?offset=' + str(page_num * 12),
		# 	callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//img[@class="img-responsive"]/@title').extract_first()
		datas = response.xpath('//div[@class="pull-left"]/h4')
		for d in datas:
			val = d.xpath('./text()').extract_first()
			if val:
				val = val.strip()
			if d.xpath('./@class').extract_first() == 'clrBrown':
				item['agent role'] = val
			else:
				item['company'] = val

		phones = response.xpath('//div[@class="col-sm-7"]//a[contains(@href,"tel:")]/text()').extract()
		if phones:
			if len(phones) == 1:
				item['mobile'] = phones[0]
			else:
				item['mobile'] = phones[0]
				item['direct number'] = phones[1]
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		email = response.xpath('//div[@class="col-sm-7"]//a[contains(@href,"mailto:")]/text()').extract_first()
		if email:
			item['email'] = email.strip()

		# socials = response.xpath('//div[@class="verticalbox-cell"]/div/table/tr')
		# for so in socials:
		# 	label = so.xpath('./td/div[@class="label"]/text()').extract_first()
		# 	if not label:
		# 		continue
		# 	if 'Phone' in label:
		# 		item['direct number'] = so.xpath('./td/a[@itemprop="telephone"]/text()').extract_first()
		# 	elif 'Mobile' in label:
		# 		item['mobile'] = so.xpath('./td/a[@itemprop="telephone"]/text()').extract_first()
		# 	elif 'Fax' in label:
		# 		item['fax'] = so.xpath('./td/div[@itemprop="faxNumber"]/text()').extract_first()
        #
		# email = response.xpath('//a[@itemprop="email"]/@href').extract_first()
		# if email:
		# 	item['email'] = email.replace('mailto:', '')

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="AgentProfile"]/text()').extract()
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








