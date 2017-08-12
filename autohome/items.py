# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class AutohomeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class KoubeiUrlItem(scrapy.Item):
    url = scrapy.Field()
    series_id = scrapy.Field()


#抓取失败项
class KoubeiFailedItem(scrapy.Item):
    # name = "koubei url crawler failed"
    url = scrapy.Field()


class KoubeiItem(scrapy.Item):
    # 各项定位
    switcher = {
        '购买车型': 'spec_name',
        '购买地点': 'address',
        '购买时间': 'buy_date',
        '裸车购买价': 'buy_price',
        '空间': 'space',
        '动力': 'power',
        '操控': 'manipulation',
        '油耗': 'fuel',
        '舒适性': 'comfort',
        '外观': 'surface',
        '内饰': 'trim',
        '性价比': 'ratio',
        '购车目的': 'purpose',
    }

    # define the fields for your item here like:
    name = scrapy.Field()

    url = scrapy.Field()
    series_id = scrapy.Field()
    series_name = scrapy.Field()
    spec_id = scrapy.Field()

    spec_name = scrapy.Field()
    address = scrapy.Field()
    buy_date = scrapy.Field()
    buy_price = scrapy.Field()

    #汽车之家八项评分
    space = scrapy.Field()
    power = scrapy.Field()
    manipulation = scrapy.Field()
    fuel = scrapy.Field()
    comfort = scrapy.Field()
    surface = scrapy.Field()
    trim = scrapy.Field()
    ratio = scrapy.Field()  #性价比

    purpose = scrapy.Field()  #购车目的

    title = scrapy.Field()
    date = scrapy.Field()

    content = scrapy.Field()
