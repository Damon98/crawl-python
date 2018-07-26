# -*- coding: utf-8 -*-
import datetime
import json
import random

import time
from urllib.parse import  urljoin

import scrapy
from lxml import etree
from scrapy import loader
from scrapy.loader.processors import MapCompose

from huxiu.items import HuxiuItem



class HxspiderSpider(scrapy.Spider):
    name = 'hxspider'
    allowed_domains = ['huxiu.com']
    start_urls = ['https://www.huxiu.com/']

    def parse(self, response):
        l = loader.ItemLoader(item=HuxiuItem(),response=response)
        l.add_xpath('title','//div[@class="mod-info-flow"]//h2//a/text()')
        l.add_xpath('url','//div[@class="mod-info-flow"]//h2//a/@href', MapCompose(lambda i: urljoin('https://www.huxiu.com', i)))
        l.add_xpath('author','//span[@class="author-name "]/text()')
        l.add_value('updata',datetime.datetime.now())
        TIME_STAMP = response.xpath ('//div[@class="get-mod-more js-get-mod-more-list transition"]/@data-last_dateline').extract()[0]
        data = {
            'huxiu_hash_code': '27ab1e6d0b9252b75cefec3c71dbcfba',
            'page':'2',
            'last_dateline': str(TIME_STAMP),
        }
        page = 2
        yield scrapy.FormRequest('https://www.huxiu.com/v2_action/article_list',formdata=data, callback=self.post_parse, meta={'page':page})
        yield l.load_item()

    def post_parse(self,response):
        page = response.meta['page'] + 1
        # time.sleep(random.randint(1,3))
        data = json.loads(response.text)
        if data :
            if 'data' in data.keys():
                html_post = data['data']
            if 'total_page' in data.keys():
                total_page = data['total_page']
            if 'last_dateline' in data.keys():
                last_dateline = data['last_dateline']
        item = HuxiuItem ()
        sel = etree.HTML(html_post)
        item['title'] = sel.xpath ('//h2//a/text()')
        # print(type(item['title']))
        item['url'] = [('https://www.huxiu.com'+ url) for url in sel.xpath('//h2//a/@href')]
        item['author'] = sel.xpath ( '//span[@class="author-name"]/text()')
        if item['title'] and item['url'] and item['author']:
            print('获取item内容出错', page - 1)
        item['updata'] =  datetime.datetime.now()

        yield item

        if page < int(total_page+1):
            data = {
                'huxiu_hash_code': '27ab1e6d0b9252b75cefec3c71dbcfba',
                'page': str(page),
                'last_dateline': str(last_dateline),
            }
            yield scrapy.FormRequest('https://www.huxiu.com/v2_action/article_list',formdata=data, callback=self.post_parse, meta={'page':page})






