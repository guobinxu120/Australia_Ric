# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request, FormRequest
import requests, json, re, csv
from collections import OrderedDict
from scrapy.http import TextResponse
from json import loads


class mcgrath_com_spider(scrapy.Spider):

	name = "reiq_com"

	total_count = 0
	use_selenium = True
	result_data_list = {}
	filepath = 'reiq_com.xlsx'
	headers = ['name', 'email', 'website', 'mobile', 'direct number', 'address', 'Areas of Practice', 'about us', 'detail url']
###########################################################

	def __init__(self, *args, **kwargs):
		super(mcgrath_com_spider, self).__init__(*args, **kwargs)


###########################################################

	def start_requests(self):
		f2 = open('reiq_com_url.csv')

		csv_items = csv.DictReader(f2)
		cat_data = {}

		for i, row in enumerate(csv_items):
			v = row['url']
			yield Request('https://www.reiq.com' + row['url'], callback=self.parseProduct)
			# break
		f2.close()
		# url = 'https://www.reiq.com/REIQ/About_Us/REIQ_Find.aspx?WebsiteKey=6dbdddab-8a36-4834-a6c4-649317c105d2&FAA=2#FAA'
		# form_data = {
		# 	'act': 'act_fgxml',
		# 	'15[offset]': '0',
		# 	'15[perpage]': '12',
		# 	'require': '0',
		# 	'fgpid': '15',
		# 	'ajax': '1'
		# }
		# yield FormRequest(url, self.parseProductList, formdata=form_data, meta={'page_num': 1}, dont_filter=True)

		# yield scrapy.Request(
		# 	url=url,
		# 	callback=self.parse1, dont_filter=True, meta={'page_num': 1})

		# #######--------- For test -----------###########
		# yield scrapy.Request(
		# 			url='https://www.bayleys.co.nz/search?SearchType=Everything&Radius=6&ListingType=None&OrderType=IsFeatured&Page=12&KeywordIsListingId=False&TabType=People&ViewType=Gallery&AuctionsOnly=False&PageSize=12',
		# 			callback=self.parseProductList, meta={'page_num': 1})
		# ################################################
	def parse1(self, response):
		products_list = response.xpath('//table[@class="rgMasterTable CaptionTextInvisible"]/tbody/tr')
		for pro in products_list:
			url = pro.xpath('./td/a/@href').extract_first()
			yield {'url': url}

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

		data_list = response.xpath('//div[@class="ReadOnly PanelField Left"]')
		for data in data_list:
			name = data.xpath('./div/span/text()').extract_first()

			if name:
				name = name.strip()

			if not name:
				continue

			vals = data.xpath('./div[@class="PanelFieldValue"]//text()').extract()
			val_list = []
			for v in vals:
				if v:
					v = v.strip()
					if v:
						val_list.append(v)
			value = ''
			if val_list:
				value = ' '.join(val_list)

			if name == 'Agent Name':
				item['name'] = value
			elif name == 'Address':
				item['address'] = value
			elif name == 'Work Phone':
				item['direct number'] = value
			elif name == 'Mobile':
				item['mobile'] = value
			elif name == 'Website':
				item['website'] = value
			elif name == 'Email':
				item['email'] = value
			elif name == 'About':
				item['about us'] = value

		data = response.xpath('//div[@id="ctl01_TemplateBody_WebPartManager1_gwpciNewQueryMenuCommon_ciNewQueryMenuCommon_ResultsGrid_Grid1"]//table[@class="rgMasterTable CaptionTextInvisible"]/tbody/tr/td/text()').extract()
		item['Areas of Practice'] = '\n'.join(data)
		item['detail url'] = response.url

		self.total_count += 1
		print('total_count: ' + str(self.total_count))
		print item
		self.result_data_list[str(self.total_count)] = item

		# yield item
		# yield item








