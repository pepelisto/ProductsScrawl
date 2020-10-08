import scrapy
from scrapers.items import ProductItem
import json, re


class CaWalmartSpider(scrapy.Spider):

    name = "ca_walmart"
    allowed_domains = ["walmart.ca"]
    start_urls = ["https://www.walmart.ca/en/grocery/fruits-vegetables/fruits/N-3852"]

    # def request(self, url, callback):
    #     """
    #      wrapper for scrapy.request
    #     """
    #     request = scrapy.Request(url=url, callback=callback)
    #     request.cookies['find-in-store-section'] = 1
    #     return request
    #
    # def start_requests(self):
    #     for i, url in enumerate(self.start_urls):
    #         yield self.request(url, self.parse)

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
                yield response.follow(url, callback=self.parse_item_details, cb_kwargs={'item': item}, headers={'find-in-store':True})

    def parse_item_details(self, response, item):
        json_fields = json.loads(response.css('script:contains("description") ::text').re_first('(.*)'))
        item['description'] = json_fields['description']
        item['name'] = json_fields['name']
        item['brand'] = json_fields['brand']['name']
        item['sku'] = json_fields['sku']
        item['image_url'] = json_fields['image'][0]



        # text = response.css('script:contains("window.__PRELOADED_STATE__") ::text').get()
        print(response.text)


        # barcodes = text[text.index('upc":[') + len('upc":['):text.index('],')]
        # print(barcodes + 'hola')
        # item['barcodes'] = barcodes
        item['store'] = 'Walmart'
        item['package'] = '1 unit'
        item['branch'] = 'BRANCH01'
        item['stock'] = 450
        item['price'] = 200
        yield item



#response.css('.evlleax2').extract()                 scrapy crawl ca_walmart              window.__PRELOADED_STATE__=    .esdkp3p0
#response.xpath('//script[10]/text()').extract()     ### en el 10 esta
#evlleax2      json.loads(response.css('script:contains("description") ::text').re_first('(.*)'))
