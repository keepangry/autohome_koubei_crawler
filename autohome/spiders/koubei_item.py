# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from autohome.items import KoubeiItem, KoubeiFailedItem
from selenium import webdriver
from autohome.pipelines import KoubeiPipeline

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import random
import math
import pymysql


def chunk(L, num):
    length = len(L)
    if length <= num:
        return L
    l = math.ceil(length/num)
    result = []
    for i in range(num):
        result.append( L[ i*l : (i+1)*l ] )
    return result


class KoubeiItemSpider(scrapy.Spider):
    name = "koubei_item"
    allowed_domains = ["k.autohome.com.cn"]
    # pipeline = set([KoubeiPipeline, ])
    # start_urls = ['http://k.autohome.com.cn/']
    base_url = 'http://k.autohome.com.cn'

    def __init__(self, limit='0-10', *args, **kwargs):
        self.start = int(limit.split('-')[0])
        self.limit = int(limit.split('-')[1])

        #启动数据库
        self.conn = pymysql.connect(host='127.0.0.1', user='spider', passwd='spider', db='spider', charset='utf8')
        self.cur = self.conn.cursor()
        super(KoubeiItemSpider, self).__init__(*args, **kwargs)
        self.chrome_init()


    def __del__(self):
        self.conn.close()
        self.cur.close()
        self.browser.quit()

    def chrome_init(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "plugins.plugins_disabled": ["Shockwave Flash"] }
        chrome_options.add_experimental_option("prefs", prefs)
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        self.browser.set_page_load_timeout(15)

    def start_requests(self):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id,url from koubei_url where status=0 limit %s,%s"%(self.start,self.limit))
        # cursor.execute("SELECT id,url from koubei_url limit %s,%s"%(self.start,self.limit))
        urls = cursor.fetchall()
        cursor.close()
        for url in urls:
            yield scrapy.Request(url=url['url'], callback=self.koubeiParse, meta={'item':url})


    def koubeiParse(self, response):
        meta = response.meta['item']
        status = 0
        try:
            item = self.koubeiHtml(response)
            #其他各项属性
            if not item:
                return
            # 写入数据库
            self.cur.execute('delete from koubei where id=%s'%(meta['id']))
            sql = "insert into koubei(id,url,content,series_id,series_name,spec_id,spec_name,address,buy_date,buy_price," \
                  "space,power,manipulation,fuel,comfort,surface,trim,ratio,purpose,title,date" \
                  ") values(" \
                  "%s,'%s','%s',%s,'%s',%s,'%s','%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,%s,'%s','%s','%s')"\
                  %(meta['id'], meta['url'], item['content'], item['series_id'], item['series_name'], item['spec_id'], item['spec_name'],
                    item['address'],item['buy_date'],item['buy_price'],item['space'],item['power'],item['manipulation'],item['fuel'],
                    item['comfort'],item['surface'],item['trim'],item['ratio'],item['purpose'],item['title'],item['date'])
            status = self.cur.execute(sql)
            if status:
                self.cur.execute("update koubei_url set status=1 where id=%s" % (meta['id']))
                # yield item
        except:
            print('爬取异常，id:', meta['id'])
        finally:
            pass
        return

    def koubeiHtml(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        # 口碑左侧信息
        mouthcon_cont_left = soup.find('div', class_='mouthcon-cont-left')
        item = KoubeiItem()
        item['url'] = response.url

        for dl_s in mouthcon_cont_left.findAll('dl'):
            item_name = dl_s.find('dt').get_text(strip=True)
            item_value = dl_s.find('dd').get_text(strip=True)
            if item_name=='购买车型':
                item['series_id'] = dl_s.findAll('a')[0].attrs['href'][1:]
                item['series_name'] = dl_s.findAll('a')[0].get_text(strip=True)
                item['spec_id'] = dl_s.findAll('a')[1].attrs['href'][6:]
            if item.switcher.get(item_name):
                item[item.switcher.get(item_name)] = item_value

        ##有可能多个内容
        mouthcons = soup.findAll('div', class_='mouth-item')
        for mouthcon in mouthcons:
            type = mouthcon.find('i', class_='icon icon-zj').get_text()
            if type == '口碑':
                koubei_content = mouthcon

        # 口碑主要内容信息
        item['date'] = koubei_content.find('div', class_='title-name name-width-01').find('b').get_text(strip=True)
        item['title'] = koubei_content.find('div', class_='kou-tit').find('h3').get_text(strip=True).lstrip("《").rstrip(
            '》')

        # 正文内容
        text_con = koubei_content.find('div', class_='text-con')
        replace_content_s_list = text_con.findAll('span')

        # 启动浏览器
        try:
            self.browser.get(response.url)
        except TimeoutException:
            #重启bower
            self.browser.quit()
            self.chrome_init()
            print("访问超时:",item['url'])
            raise Exception("访问超时")
            return;

        # 等待完成
        first_class = replace_content_s_list[0].attrs['class'][0]
        element_present = EC.presence_of_element_located((By.CLASS_NAME, first_class))
        WebDriverWait(self.browser, 1).until(element_present)

        # 字典，存储获取过的内容
        span_class_dict = {}
        for replace_span_s in replace_content_s_list:
            cls = replace_span_s.attrs['class'][0]
            if cls not in span_class_dict:
                script = "return window.getComputedStyle(document.getElementsByClassName('%s')[0],'before').getPropertyValue('content')" % (
                cls)
                trans = self.browser.execute_script(script).strip('\"')
                span_class_dict[cls] = trans
            replace_span_s.replace_with(span_class_dict[cls])

        # 清除style和script
        [i.extract() for i in koubei_content.findAll('style')]
        [i.extract() for i in koubei_content.findAll('script')]

        item['content'] = koubei_content.get_text(strip=True)
        print("爬去成功：",item['title'],item['url'])
        # self.browser.quit()
        return item

