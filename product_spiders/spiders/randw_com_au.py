# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "randw_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'randw_com_au.xlsx'
	headers = ['name', 'office', 'agent role', 'email', 'mobile', 'direct number', 'fax number', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		url = 'https://www.randw.com.au/find-an-agent.html'
		form_data = {
			'act': 'act_fgxml',
			'15[offset]': '0',
			'15[perpage]': '12',
			'require': '0',
			'fgpid': '15',
			'ajax': '1'
		}
		yield FormRequest(url, self.parseProductList, formdata=form_data, meta={'page_num': 1}, dont_filter=True)

		# yield scrapy.Request(
		# 	url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=1&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 	callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################

	def parseProductList(self, response):
		try:
			products_list = response.xpath('//rows/row')

			if not products_list:
				return
			for pro in products_list:
				name = pro.xpath('./name/text()').extract_first()
				agent_role = pro.xpath('./position/text()').extract_first()
				office = pro.xpath('./office/text()').extract_first()
				url = pro.xpath('./url/text()').extract_first()

				email = pro.xpath('./email/text()').extract_first()
				if url:
					if 'http' not in url:
						url = response.urljoin(url)
					yield scrapy.Request(
							url=url,
							callback=self.parseProduct, dont_filter=True, meta={'name': name,
																				'agent_role': agent_role,
																				'email': email,
																				'office':office})
				# else:
				# 	self.total_count += 1
				# 	print('total_count: ' + str(self.total_count))
				# 	# print item
				# 	self.result_data_list[str(self.total_count)] = item
				# break
		except:

			i = 1
			i +=1

			return

		page_num = response.meta['page_num'] + 1
		form_data = {
			'act': 'act_fgxml',
			'15[offset]': str(12 * (page_num - 1)),
			'15[perpage]': '12',
			'require': '0',
			'fgpid': '15',
			'ajax': '1'
		}
		yield FormRequest('https://www.randw.com.au/find-an-agent.html', self.parseProductList, formdata=form_data, meta={'page_num': page_num}, dont_filter=True)


	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.meta['name']
		item['agent role'] = response.meta['agent_role']
		item['email'] = response.meta['email']
		item['office'] = response.meta['office']
		# site = response.xpath('//p/a[@target="_blank"]/text()').extract_first()
		# if site:
		# 	if 'http' in site:
		# 		item['website'] = site
		# for_company = response.xpath('//div[@class="agent-profile-content font-14"]/a/h4/text()').extract()
		# cs = []
		# for fff in for_company:
		# 	if fff:
		# 		fff = fff.strip()
		# 		if fff:
		# 			cs.append(fff)
		# if cs:
		# 	item['company'] = '\n'.join(cs)
		tels = response.xpath('//a[@itemprop="telephone"]/text()').extract()
		if len(tels) > 0:
			item['mobile'] = tels[0]
		if len(tels) > 1:
			item['direct number'] = tels[1]

		item['fax number'] = response.xpath('//div[@itemprop="faxNumber"]/text()').extract_first()

		# address = response.xpath('//div[@class="ibox-content font-14"]/p[@class="text-primary"]/a/text()').extract_first()
        #
        #
		# item['address'] = address
		# # item['direct number'] = response.xpath('//span[@itemprop="telephone"]/text()').extract_first()
		# item['streetAddress'] = response.xpath('//p/span[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//p/span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//p/span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//p/span[@itemprop="postalCode"]/text()').extract_first()

		profiles = response.xpath('//div[@id="mlk-12"]//text()').extract()
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








