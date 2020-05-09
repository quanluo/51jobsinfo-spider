# -*- coding: utf-8 -*-
import scrapy
from tongscrapy.items import TongscrapyItem

class Py51jobsSpider(scrapy.Spider):
    name = 'py51jobs'
    #allowed_domains = ['51jobs.com']
    start_urls = ['https://search.51job.com/list/000000,000000,0000,00,9,99,python,2,1.html']

    def parse(self, response):
        item = TongscrapyItem()
        for i in range(4, 45):
            item['position'] = response.xpath('//*[@id="resultList"]/div[{num}]/p/span/a/text()'.format(num=i), first=True).extract_first().strip()
            item['company'] = response.xpath('//*[@id="resultList"]/div[{num}]/span[1]/a/text()'.format(num=i), first=True).extract_first()
            item['place'] = response.xpath('//*[@id="resultList"]/div[{num}]/span[2]/text()'.format(num=i), first=True).extract_first()
            item['salary'] = response.xpath('//*[@id="resultList"]/div[{num}]/span[3]/text()'.format(num=i), first=True).extract_first()
            print('抓取完毕一条')
            yield item
        for i in range(2, 10):
            url = 'https://search.51job.com/list/000000,000000,0000,00,9,99,python,2,'+str(i)+'.html'
            yield scrapy.Request(url, callback=self.parse)
            print('抓取完毕一页')