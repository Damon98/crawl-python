import scrapy
from xiaohua.items import XiaohuaItem
import time
import re

class XiaohuaSpider(scrapy.Spider):
    name = 'xiaohua'
    allowed_domains=['mmonly.cc']
    start_urls=['http://www.mmonly.cc/tag/xh1/index.html']

    def parse(self,response):
        mm_links= response.xpath('//div[@class="item masonry_brick masonry-brick"]//a[@target="_blank"]/@href').extract() #各位MM的主页链接
        for link in mm_links:
            request1 = scrapy.Request(link,callback=self.parse_item)
            time.sleep(1)
            yield request1
        for link in mm_links:
            request2 = scrapy.Request(link, callback=self.parse_last)
            time.sleep(1)
            yield request2
        page_set = 2
        if page_set <= 7:
            url = 'http://www.mmonly.cc/tag/xh1/' + str(page_set) + '.html'
            page_set +=1
            request3 = scrapy.Request(url, callback=self.parse)
            time.sleep(1)
            yield request3

    def parse_item(self,response):
        get_page = response.xpath('//div[@class="pages"]//a[1]/text()').extract()[0].strip() #/html/body/div[2]/div[2]/div[8]/ul/li[1]/a
        if get_page != '':
            get_page = int(re.findall((r'\d+'),get_page[0])[0])
        for i in range(2,get_page+1):
            mm_url = response.url[:-5] + '_' + str(i) + '.html'
            request4 = scrapy.Request(mm_url, callback=self.parse_last)
            time.sleep(1)
            yield request4

    def parse_last(self,response):
        item = XiaohuaItem()
        item['alt'] = response.xpath('//div[@id="big-pic"]//img/@alt').extract()[0].strip()
        image_links = response.xpath('//div[@id="big-pic"]//img/@src').extract()
        item['src']=[]
        for src in image_links:
            if '.jpg' in src:
                item['src'].append(src)

        yield item

        #http://www.mmonly.cc/tstx/ylxw/218051.html





