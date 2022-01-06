# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "wiseberry_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'wiseberry_com_au.xlsx'
	headers = ['name', 'agent role', 'email', 'phone', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.wiseberry.com.au/find-agent?offset=0&limit=12&paginate=1',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 0})

	def parseProductList(self, response):
		try:
			products_list = loads(response.body)['team']
			# products_list = response.xpath('//div[@class="fluidgrid-cell fluidgrid-cell-2 fluidgrid-cell-nopadding fluidgrid-cell-nomargin"]/div')

			if not products_list:
				return
			for pro in products_list:
				identifier = pro['identifier']
				slug = pro['slug']
				ref = pro['ref']


				url = 'https://www.wiseberry.com.au/{}/team/member/{}/{}'.format(identifier, slug, ref)
				if url:
					if 'http' not in url:
						url = response.urljoin(url)

					name = pro['cname']
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True,
						meta={
							'name':name
						})
				# break
		except:

			i = 1
			i +=1

		page_num = response.meta['page_num'] + 1
		yield scrapy.Request(
			url='https://www.wiseberry.com.au/find-agent?offset={}&limit=12&paginate=1'.format(str(page_num * 12)),
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.meta['name']
		# company = response.meta['company']
		# item['company'] = company

		item['agent role'] = response.xpath('//div[@class="conceptContent"]/p/text()').extract_first()

		# phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		# item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		conceptContent = response.xpath('//div[@class="conceptContent"]/p/a/text()').extract()
		for so in conceptContent:
			# label = so.xpath('./td/div[@class="label"]/text()').extract_first()
			if not so:
				continue
			if '@' in so:
				item['email'] = so
			else:
				item['phone'] = so


		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="col-md-8"]/p/text()').extract()
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








