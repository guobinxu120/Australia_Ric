# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "eldersrealestate_com_au"

	total_count = 0
	use_selenium = False
	result_data_list = {}
	filepath = 'eldersrealestate_com_au.xlsx'
	headers = ['name', 'agent role', 'company', 'email', 'mobile', 'direct number']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		yield scrapy.Request(
			url='https://www.eldersrealestate.com.au/find-an-agent/',
			callback=self.parseProductList, dont_filter=True, meta={'page_num': 1})

	def parseProductList(self, response):
		page_num = response.meta['page_num'] + 1
		try:
			if page_num == 2:
				products_list = response.xpath('//div[@class="team-grid__inner row"]/div/div')
			else:
				data_str = json.loads(response.body)
				if 'data' in data_str.keys():
					data = data_str['data']
					resp1 = TextResponse(url=response.url,
                                body=data,
                                encoding='utf-8')
					products_list = resp1.xpath('//div[@class="team-grid__inner row"]/div/div')
				else:
					return

			if not products_list:
				return
			for pro in products_list:
				item = OrderedDict()

				for h in self.headers:
					item[h] = ''

				item['name'] = pro.xpath('.//h4[@class="team-card__name"]/text()').extract_first()
				item['company'] = pro.xpath('.//strong[@class="team-card__agency"]/text()').extract_first()

				item['agent role'] = pro.xpath('.//span[@class="team-card__position"]/text()').extract_first()
				item['email'] = pro.xpath('.//li[@class="team-card__contact__item team-card__contact__item--email"]/a/text()').extract_first()
				item['mobile'] = pro.xpath('.//li[@class="team-card__contact__item team-card__contact__item--phone team-card__contact__item--mobile"]/a/text()').extract_first()
				item['direct number'] = pro.xpath('.//li[@class="team-card__contact__item team-card__contact__item--phone team-card__contact__item--bh"]/a/text()').extract_first()
				# item['detail url'] = pro.xpath('.//figure[@class="team-card__figure"]/a/@href').extract_first()

				self.total_count += 1
				print('total_count: ' + str(self.total_count))
				print item
				self.result_data_list[str(self.total_count)] = item
		except:

			i = 1
			i +=1


		yield scrapy.Request(
			url='https://www.eldersrealestate.com.au/wp-admin/admin-ajax.php?action=find_an_agent&page=' + str(page_num),
			callback=self.parseProductList, dont_filter=True, meta={'page_num': page_num})

	def parseProduct(self, response):


		item = OrderedDict()

		for h in self.headers:
			item[h] = ''

		item['name'] = response.xpath('//h1[@id="mlk-4"]/text()').extract_first()
		company = response.meta['company']
		item['company'] = response.xpath('//div[@id="mlk-15"]/text()').extract_first()

		item['agent role'] = response.xpath('//h3[@id="mlk-5"]/text()').extract_first()

		# phone = response.xpath('//a[@class="phone"]/text()').extract_first()
		# if phone:
		# 	phone = phone.strip()
		# item['direct number'] = phone
		# item['mobile'] = response.xpath('//a[@class="mobile"]/text()').extract_first()
		# item['email'] = response.xpath('//a[@class="email"]/text()').extract_first()

		socials = response.xpath('//div[@class="verticalbox-cell"]/div/table/tr')
		for so in socials:
			label = so.xpath('./td/div[@class="label"]/text()').extract_first()
			if not label:
				continue
			if 'Phone' in label:
				item['direct number'] = so.xpath('./td/a[@itemprop="telephone"]/text()').extract_first()
			elif 'Mobile' in label:
				item['mobile'] = so.xpath('./td/a[@itemprop="telephone"]/text()').extract_first()
			elif 'Fax' in label:
				item['fax'] = so.xpath('./td/div[@itemprop="faxNumber"]/text()').extract_first()

		email = response.xpath('//a[@itemprop="email"]/@href').extract_first()
		if email:
			item['email'] = email.replace('mailto:', '')

		# item['streetAddress'] = response.xpath('//div[@itemprop="streetAddress"]/text()').extract_first()
		# item['addressLocality'] = response.xpath('//span[@itemprop="addressLocality"]/text()').extract_first()
		# item['addressRegion'] = response.xpath('//span[@itemprop="addressRegion"]/text()').extract_first()
		# item['postalCode'] = response.xpath('//span[@itemprop="postalCode"]/text()').extract_first()




		profiles = response.xpath('//div[@class="fluidgrid-group fluidgrid-group-none"]//div[@class="fluidgrid-cell fluidgrid-cell-4"]/div/div/text()').extract()
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








