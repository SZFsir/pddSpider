# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PddcommentsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    review_id = scrapy.Field()
    desc_score = scrapy.Field()
    logistics_score = scrapy.Field()
    service_score = scrapy.Field()
    specs = scrapy.Field()
    avatar = scrapy.Field()
    avatar_hash = scrapy.Field()
    name = scrapy.Field()
    goods_id = scrapy.Field()
    comment = scrapy.Field()
    stars = scrapy.Field()
    opt = scrapy.Field()


