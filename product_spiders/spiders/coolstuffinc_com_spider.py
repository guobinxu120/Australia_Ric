# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from collections import OrderedDict


class coolstuffinc_comSpider(scrapy.Spider):

	name = "coolstuffinc_com_spider"

	# use_selenium = False
	domain = 'https://www.coolstuffinc.com/'
	total_count = 0
	categories_data = None
	result_data_list = {}
	custom_settings = {
        'CONCURRENT_REQUESTS': 8,
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
        'CONCURRENT_REQUESTS_PER_IP': 4
    }

	headers = ['PageUrl', 'ProductLink', 'ImageLink', 'Rarity', 'ProductTitle', 'NewQty', 'NewPrice', 'NewContent', 'NearMintQty', 'NearMintPrice', 'NearMintContent',
			   'FoilNearMintQty', 'FoilNearMintPrice', 'FoilNearMintContent',
			   'PlayedQty', 'PlayedPrice', 'PlayedContent', 'FoilPlayedQty', 'FoilPlayedPrice', 'FoilPlayedContent', 'SetName']


###########################################################

	def __init__(self, *args, **kwargs):
		super(coolstuffinc_comSpider, self).__init__(*args, **kwargs)
###########################################################

	def start_requests(self):
		filename = "basic_data/categories_csi.txt"
		with open(filename, 'U') as f:

			for category_url in f.readlines():
				cat_name = category_url.strip().split('/')[-1]
				self.result_data_list[cat_name] = []

				yield scrapy.Request(
					url=category_url.strip(),
					callback=self.parse_category, meta={'cat': cat_name})

	def parse_category(self, response):

		for subcategory_node in response.xpath('//ul[contains(@class,"set-group")]/li/a'):

			subcategory_url = subcategory_node.xpath('./@href').extract_first()
			set_name = subcategory_node.xpath('./text()').extract_first()

			if subcategory_url:
				subcategory_url = response.urljoin( subcategory_url )

			yield scrapy.Request( url=subcategory_url, callback=self.parseProductList, meta={'set_name': set_name, 'cat': response.meta['cat'] } )


			####------------- test ----------------###
			# if subcategory_url == 'https://www.coolstuffinc.com/page/449':#?&resultsperpage=25&page=2':
			# 	yield scrapy.Request( url=subcategory_url, callback=self.parseProductList, meta={'set_name': set_name } )
			#####################################################

	def parseProductList(self, response):
		domain = 'https://www.coolstuffinc.com'
		products_list = response.xpath('//div[@id="mainContent"]//div[@itemtype="http://schema.org/Product"]')

		for product in products_list:

			item = OrderedDict()

			item['PageUrl'] = response.url

			item['ProductLink'] = response.urljoin(product.xpath('.//a[@itemprop="url"]/@href').extract_first())
			item['ImageLink'] = product.xpath('.//*[@itemprop="image"]/@src').extract_first()

			rarity = product.xpath('.//div[@class="large-12 medium-12 small-12" and contains(text(), "Rare")]/text()').extract_first()
			item['Rarity'] = ''
			if rarity:
				item['Rarity'] = rarity
			item['ProductTitle'] = product.xpath('.//span[@itemprop="name"]/text()').extract_first()

			item['NewQty'] = ''
			item['NewPrice'] = ''
			item['NewContent'] = ''

			item['NearMintQty'] = ''
			item['NearMintPrice'] = ''
			item['NearMintContent'] = ''

			item['FoilNearMintQty'] = ''
			item['FoilNearMintPrice'] = ''
			item['FoilNearMintContent'] = ''

			item['PlayedQty'] = ''
			item['PlayedPrice'] = ''
			item['PlayedContent'] = ''

			item['FoilPlayedQty'] = ''
			item['FoilPlayedPrice'] = ''
			item['FoilPlayedContent'] = ''

			userTables = product.xpath('.//*[@itemprop="offers"]')

			for tr_tag in userTables:
				tr_tag_title = ''.join(tr_tag.xpath('.//*[@class="row"]/text()').extract()).strip()

				qty = tr_tag.xpath('.//*[@class="card-qty"]/text()').re(r'[\d\+]+')
				if qty:
					qty = qty[0]
				else:
					qty = ''
				price = tr_tag.xpath('.//*[@itemprop="price"]/b/text()').extract_first()
				if not price:
					price = tr_tag.xpath('.//*[@itemprop="price"]/text()').extract_first()
				content = tr_tag.xpath('.//*[@itemprop="offers"]/text()').extract_first()
				if content:
					content = content.strip().encode('utf-8')

				if tr_tag_title == 'New':
					item['NewQty'] = qty
					item['NewPrice'] = price
					item['NewContent'] = content
				elif tr_tag_title == 'Near Mint':
					item['NearMintQty'] = qty
					item['NearMintPrice'] = price
					item['NearMintContent'] = content
				elif tr_tag_title == 'Foil Near Mint':
					item['FoilNearMintQty'] = qty
					item['FoilNearMintPrice'] = price
					item['FoilNearMintContent'] = content
				elif tr_tag_title == 'Played':
					item['PlayedQty'] = qty
					item['PlayedPrice'] = price
					item['PlayedContent'] = content
				elif tr_tag_title == 'Foil Played':
					item['FoilPlayedQty'] = qty
					item['FoilPlayedPrice'] = price
					item['FoilPlayedContent'] = content

			if not response.meta['set_name']:
				response.meta['set_name'] = response.meta['set_name']

			item['SetName'] = response.meta['set_name']

			self.total_count += 1
			print('total_count: ' + str(self.total_count))
			print(item)
			self.result_data_list[response.meta['cat']].append(item)
			# yield item

		nextLink = response.xpath('//*[@id="nextLink"]/a/@href').extract_first()
		if nextLink:
			yield Request(response.urljoin(nextLink), callback=self.parseProductList, meta=response.meta)







