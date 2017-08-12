# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
from autohome.items import KoubeiItem, KoubeiFailedItem, KoubeiUrlItem
import pymysql

class AutohomePipeline(object):
    def process_item(self, item, spider):
        return item


class KoubeiPipeline(object):
    def __init__(self):
        pass

    def process_item(self, item, spider):
        if isinstance(item, KoubeiItem):
            # file = codecs.open('data/koubei/series/%s.jl'%(item['series_name']), 'a', encoding='utf-8')
            with open('data/koubei/series/%s.jl'%(item['series_name']),'a') as file:
                line = json.dumps(dict(item), ensure_ascii=False) + "\n"
                file.write(line)
            return item
        elif isinstance(item, KoubeiFailedItem):
            with open('data/koubei/failed/koubei_failed_url.jl', 'a') as file:
                line = json.dumps(dict(item), ensure_ascii=False) + "\n"
                file.write(line)
            return item
        else:
            pass

    def spider_closed(self, spider):
        pass


class KoubeiUrlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', user='spider', passwd='spider', db='spider', charset='utf8')
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        if isinstance(item, KoubeiUrlItem):
            sql = ("insert into koubei_url_1(url,series_id,batch) values(%s,%s,%s)")
            lis = (item['url'],item['series_id'], '1')
            status = self.cur.execute(sql, lis)
            return item
        else:
            pass

    def spider_closed(self, spider):
        self.conn.close()
        self.cur.close()
