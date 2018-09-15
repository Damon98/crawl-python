# -*- coding: utf-8 -*-
import json
import re
from urllib.parse import urlencode

import scrapy
from scrapy import Request

from jdGoods.items import JdgoodsItem
from jdGoods.settings import KEYWORD, TOTAL_PAGE, BRAND


class JczSpider(scrapy.Spider):
    name = 'jcz'
    oddpages = [i for i in range (1, TOTAL_PAGE*2, 2) if i % 2 == 1]
    evenpages =[i for i in range (2, TOTAL_PAGE*2+2, 2)]
    oddcounts = [i for i in range (1, TOTAL_PAGE*60, 60) if i % 2 == 1]
    evencounts = [i for i in range (31, TOTAL_PAGE*60+30, 60) if i % 2 == 1]
    start_urls = []
    for i in range(len(oddpages)):
        odd_params = {
            'keyword': KEYWORD,
            'enc': 'utf - 8',
            'qrst': '1',
            'rt': '1',
            'stop': '1',
            'vt': '2',
            # 'stock': '1'
            # 'wq': KEYWORD,
            # 'psort': '4',
            'page': str(oddpages[i]),
            's': str(oddcounts[i]),
            'click': '0',
            'ev': 'exbrand_'+BRAND+'^',
        }
        start_urls.append('https://search.jd.com/search?' + urlencode(odd_params))

    def parse(self, response):
        ids = response.xpath('//*[@id="J_goodsList"]/ul//li/@data-sku').extract()
        # 构造页面中第二部分内容请求链接
        id_string = []
        for i in range (len (ids)):
            if i == len (ids) - 1:
                id_string.append (ids[i])
            else:
                id_string.append (ids[i] + ',')
        ids_params = id_string[0]
        for i in range (1, len (ids)):
            ids_params += id_string[i]
        for i in range (len (self.evenpages)):
            even_params = {
                'keyword':KEYWORD,
                'enc': 'utf-8',
                'qrst': '1',
                'rt': '1',
                'stop': '1',
                'vt': '2',
                # 'wq': KEYWORD,
                'ev': 'exbrand_'+BRAND+'^',
                # 'psort': '4',
                'page': str(self.evenpages[i]),
                's': str(self.evencounts[i]),
                'scrolling': 'y',
                # 'log_id': '1534473244.56026',# 1534488516624
                'tpl': '1_M',
                'show_items': ids_params
            }
            url = 'https://search.jd.com/search?' + urlencode(even_params)
            yield Request(url, meta={'ids': ids}, callback=self.item_parse)
        pass

    def item_parse(self, response):
        id2 = response.xpath ('//*[@id="J_goodsList"]/ul//li/@data-sku').extract ()
        id1 = response.meta['ids']
        ids = id1 + id2
        for id in ids:
            url_good = 'https://club.jd.com/review/' + id + '-3-1-3.html'
            url_gen = 'https://club.jd.com/review/' + id + '-3-1-2.html'
            url_poor = 'https://club.jd.com/review/' + id + '-3-1-1.html'
            comment_sum = 'https://club.jd.com/comment/productCommentSummaries.action?referenceIds=' + id
            url_price = 'https://p.3.cn/prices/mgets?&skuids=J_'+id+'&type=1'
            yield Request(url_good, callback=self.comment_parse_good, meta={'id':id})
            yield Request(url_gen, callback=self.comment_parse_gen, meta={'id':id})
            yield Request(url_poor, callback=self.comment_parse_poor, meta={'id':id})
            yield Request(comment_sum, callback=self.comment_parse_sum, meta={'id':id})
            yield Request(url_price, callback=self.price_parse, meta={'id':id})

    def comment_parse_good(self,response):
        item = JdgoodsItem()
        ProductId = response.meta['id']
        item['ProductId'] = ProductId
        item['Goods_name'] = response.xpath('//*[@id="product-info"]//ul/li[@class="p-name"]/a/text()').extract()
        try:
            item['ProductBrand'] = re.search('(.*?),|,', response.xpath('/html/head/meta[@name="keywords"]/@content').extract()[0]).group(1)
        except Exception:
            item['ProductBrand'] = response.xpath('/html/head/meta[@name="keywords"]/@content').extract()
        item['ProductUrl'] = 'https://item.jd.com/' + ProductId + '.html'
        good_comments = []
        good_comments_list = response.xpath('//*[@id="comments-list"]//div[@class="mc"]')
        flag = 1
        for each in good_comments_list:
            comnent = {}
            comnent['user_name_No.' + str (flag)] = each.xpath (
                'normalize-space(.//div[@class="u-name"]/text())').extract ()
            comnent['user_comment_No.' + str (flag)] = each.xpath (
                'normalize-space(.//div[@class="comment-content"]/dl/dd/text())').extract ()
            comnent['user_commentDate_No.' + str (flag)] = each.xpath (
                'normalize-space(.//span[@class="date-comment"]/a/text())').extract ()
            comnent['user_star_No.' + str (flag)] = '5'
            good_comments.append(comnent)
            flag += 1
        item['good_comments'] = good_comments
        yield item


    def comment_parse_gen(self, response):
        item = JdgoodsItem()
        ProductId = response.meta['id']
        item['ProductId'] = ProductId
        gen_comments = []
        gen_comments_list = response.xpath('//*[@id="comments-list"]//div[@class="mc"]')
        flag = 1
        for each in gen_comments_list:
            comnent = {}
            comnent['user_name_No.' + str (flag)] = each.xpath (
                'normalize-space(.//div[@class="u-name"]/text())').extract ()
            comnent['user_comment_No.' + str (flag)] = each.xpath (
                'normalize-space(.//div[@class="comment-content"]/dl/dd/text())').extract ()
            comnent['user_commentDate_No.' + str (flag)] = each.xpath (
                'normalize-space(.//span[@class="date-comment"]/a/text())').extract ()
            comnent['user_star_No.' + str (flag)] = '3'
            gen_comments.append(comnent)
            flag += 1
        item['gen_comments'] = gen_comments
        yield item

    def comment_parse_poor(self, response):
        item = JdgoodsItem()
        ProductId = response.meta['id']
        item['ProductId'] = ProductId
        poor_comments = []
        poor_comments_list = response.xpath('//*[@id="comments-list"]//div[@class="mc"]')
        flag = 1
        for each in poor_comments_list:
            comnent = {}
            comnent['user_name_No.' + str (flag)] = each.xpath (
                'normalize-space(.//div[@class="u-name"]/text())').extract ()
            comnent['user_comment_No.' + str (flag)] = each.xpath (
                'normalize-space(.//div[@class="comment-content"]/dl/dd/text())').extract ()
            comnent['user_commentDate_No.' + str (flag)] = each.xpath (
                'normalize-space(.//span[@class="date-comment"]/a/text())').extract ()
            comnent['user_star_No.' + str (flag)] = '1'
            poor_comments.append(comnent)
            flag += 1
        item['poor_comments'] = poor_comments
        yield item

    def comment_parse_sum(self, response):
        item = JdgoodsItem ()
        ProductId = response.meta['id']
        item['ProductId'] = ProductId
        if response.text:
            results = json.loads(response.text)
            if 'CommentsCount' in results.keys():
                for field in results['CommentsCount'][0].keys():
                    if field in item.fields:
                        if field != 'ProductId':
                            item[field] = results['CommentsCount'][0][field]
                            yield item

    def price_parse(self,response):
        item = JdgoodsItem ()
        ProductId = response.meta['id']
        item['ProductId'] = ProductId
        if response.text:
            content = response.text
            if content:
                pass
                results = json.loads(content)[0]
                if 'p' in results.keys ():
                    item['Goods_price'] = results['p']
                    yield item



