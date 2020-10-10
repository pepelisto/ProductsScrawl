import scrapy
from scrapers.items import ProductItem
import json, re
from pprint import pprint

class CaWalmartSpider(scrapy.Spider):

    name = "ca_walmart"
    allowed_domains = ["walmart.ca"]
    page_number = 2
    i = 0 #initial store
    start_urls = [
        "https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852",  #### solo esta buscando el primero
        "https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852/",
    ]
    interest_stores = [
        ['Toronto Stockyards Supercentre', '3106', 'https://www.walmart.ca/api/product-page/find-in-store?latitude=43.6562281&longitude=-79.4377713&lang=en&upc='], #### solo esta buscando el primero
        ['Thunder Bay Supercentre', '3124', 'https://www.walmart.ca/api/product-page/find-in-store?latitude=48.4128517&longitude=-89.2419269&lang=en&upc=']
    ]
    def start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse(self, response):
        i = CaWalmartSpider.interest_stores[CaWalmartSpider.i]
        all_items = response.css('article')
        for product in all_items:
            link = product.css('a.product-link::attr(href)').get()
            if link != None:
                item = ProductItem()
                url = 'https://www.walmart.ca' + link
                item['url'] = url
                text = response.css('script:contains("catPageTrail") ::text').get()
                category = text[text.index('catPageTrail: [') + len('catPageTrail: ['):text.index('],')]
                category1 = category.replace('"','')
                item['category'] = str(category1.replace(',',' - '))
                yield response.follow(url, callback=self.parse_item_details, cb_kwargs={'item': item, 'i': i})


    def parse_item_details(self, response, item, i):
        json_fields = json.loads(response.css('script:contains("description") ::text').re_first('(.*)'))
        item['description'] = json_fields['description']
        item['name'] = json_fields['name']
        item['brand'] = json_fields['brand']['name']
        item['sku'] = json_fields['sku']
        item['image_url'] = json_fields['image'][0]
        item['package'] = response.css('.eudvd6x0::text').get()
        text = response.css('script:contains("window.__PRELOADED_STATE__") ::text').get()
        barcodes = text.split('upc":[')
        barcodes = barcodes[1]
        barcodes = barcodes.split(']')
        barcodes = barcodes[0]
        barcodes_array = barcodes.split(',')
        barcode_to_url_price = barcodes_array[0].replace('"','')
        url2 = i[2] + barcode_to_url_price
        item['barcodes'] = barcodes
        item['store'] = 'Walmart'
        item['branch'] = i[1]

        yield response.follow(url2, callback=self.parse_item_price_details, cb_kwargs={'item': item, 'i': i})

    def parse_item_price_details(self, response, item, i):
        result = json.loads(response.body)
        for inf in result['info']:
            if inf['displayName'] == i[0]:
                item['stock'] = inf['availableToSellQty']
                item['price'] = inf['sellPrice']
        yield item
        next_page = "https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852/page-" + str(CaWalmartSpider.page_number)
        if CaWalmartSpider.page_number < 3:
            CaWalmartSpider.page_number += 1
            yield response.follow(next_page, callback=self.parse)
        CaWalmartSpider.page_number = 2
        CaWalmartSpider.i += 1






#response.css('.evlleax2').extract()                 scrapy crawl ca_walmart              window.__PRELOADED_STATE__=    .esdkp3p0
#response.xpath('//script[10]/text()').extract()     ### en el 10 esta
#evlleax2      json.loads(response.css('script:contains("description") ::text').re_first('(.*)'))
