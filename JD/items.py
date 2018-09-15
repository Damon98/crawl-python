# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field


class JdgoodsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    ProductId = Field()
    ProductBrand = Field()
    ProductUrl = Field()
    CommentCount = Field()
    DefaultGoodCount = Field()
    GeneralCount = Field()
    GeneralRate = Field()
    GoodCount = Field()
    GoodRate = Field()
    PoorCount = Field()
    PoorRate = Field()
    Goods_name = Field()
    Goods_price = Field()

    good_comments = Field()
    gen_comments = Field()
    poor_comments = Field()

    pass
