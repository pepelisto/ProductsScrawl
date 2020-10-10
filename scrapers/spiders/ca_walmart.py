import scrapy
from scrapers.items import ProductItem
import json, re
from pprint import pprint


class CaWalmartSpider(scrapy.Spider):

    name = "ca_walmart"
    allowed_domains = ["walmart.ca"]
    start_urls = ["https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852"]


    def parse(self, response):
        all_items = response.css('article')
        for product in all_items:
            link = product.css('a.product-link::attr(href)').get()
            if link != None:
                item = ProductItem()
                url = 'https://www.walmart.ca' + link
                item['url'] = url
                # item['price'] = product.css('.price-current div::text').get()
                text = response.css('script:contains("catPageTrail") ::text').get()
                category = text[text.index('catPageTrail: [') + len('catPageTrail: ['):text.index('],')]
                category1 = category.replace('"','')
                item['category'] = str(category1.replace(',',' - '))
                yield response.follow(url, callback=self.parse_item_details, cb_kwargs={'item': item})

    def parse_item_details(self, response, item):
        json_fields = json.loads(response.css('script:contains("description") ::text').re_first('(.*)'))
        item['description'] = json_fields['description']
        item['name'] = json_fields['name']
        item['brand'] = json_fields['brand']['name']
        item['sku'] = json_fields['sku']
        item['image_url'] = json_fields['image'][0]

        text = response.css('script:contains("window.__PRELOADED_STATE__") ::text').get()
        barcodes = text.split('upc":[')
        barcodes = barcodes[1]
        barcodes = barcodes.split(']')
        barcodes = barcodes[0]
        barcodes_array = barcodes.split(',')
        barcode_to_url_price = barcodes_array[0].replace('"','')
        url2 = 'https://www.walmart.ca/api/product-page/find-in-store?latitude=43.60822&longitude=-79.69387&lang=en&upc=' + barcode_to_url_price
        print(barcode_to_url_price)
        item['barcodes'] = barcodes
        item['store'] = 'Walmart'
        item['package'] = '1 unit'
        item['branch'] = '3124'

        yield response.follow(url2, callback=self.parse_item_price_details, cb_kwargs={'item': item})

    def parse_item_price_details(self, response, item):
        interest_centers = 'Heartland Supercentre'
        result = json.loads(response.body)
        # pprint(result['info'])
        for i in result['info']:
            if i['displayName'] == interest_centers:
                item['stock'] = i['availableToSellQty']
                item['price'] = i['sellPrice']
        yield item



#response.css('.evlleax2').extract()                 scrapy crawl ca_walmart              window.__PRELOADED_STATE__=    .esdkp3p0
#response.xpath('//script[10]/text()').extract()     ### en el 10 esta
#evlleax2      json.loads(response.css('script:contains("description") ::text').re_first('(.*)'))
