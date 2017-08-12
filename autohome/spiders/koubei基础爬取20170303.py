# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from autohome.items import KoubeiItem, KoubeiFailedItem
from selenium import webdriver
from autohome.pipelines import KoubeiPipeline

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By




class KoubeiSpider(scrapy.Spider):
    name = "koubei_back"
    allowed_domains = ["k.autohome.com.cn"]
    pipeline = set([KoubeiPipeline, ])
    # start_urls = ['http://k.autohome.com.cn/']

    def start_requests(self):
        urls = [
            # 'http://k.autohome.com.cn/135/',
            #待附加口碑
            # 'http://k.autohome.com.cn/spec/26931/view_1443546_1.html?st=3&piap=0|496|0|0|1|0|0|0|0|0|1',
            # 'http://k.autohome.com.cn/spec/28541/view_1425021_1.html?st=1&piap=0|135|0|0|1|0|0|0|0|0|1',
            'http://k.autohome.com.cn/496/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.urlParse)
            # yield scrapy.Request(url=url, callback=self.koubeiParse)

    def urlParse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        titles = soup.findAll('div', class_='cont-title fn-clear')
        for title in  titles:
            url = title.find('a').attrs['href']
            yield scrapy.Request(url=url, callback=self.koubeiParse)


    def koubeiParse(self, response):
        try:
            yield self.koubeiHtml(response)
        except:
            item = KoubeiFailedItem(url=response.url)
            yield item

    def koubeiHtml(self, response):
        soup = BeautifulSoup(response.text, 'lxml')

        # 口碑左侧信息
        mouthcon_cont_left = soup.find('div', class_='mouthcon-cont-left')
        item = KoubeiItem()
        item['url'] = response.url

        for dl_s in mouthcon_cont_left.findAll('dl'):
            item_name = dl_s.find('dt').get_text(strip=True)
            item_value = dl_s.find('dd').get_text(strip=True)
            if item.switcher.get(item_name):
                item[item.switcher.get(item_name)] = item_value

        ##有可能多个内容
        mouthcons = soup.findAll('div', class_='mouth-item')
        # koubei_content = mouthcons[0]
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
        browser = webdriver.Chrome()
        browser.get(response.url)

        # 等待完成
        first_class = replace_content_s_list[0].attrs['class'][0]
        element_present = EC.presence_of_element_located((By.CLASS_NAME, first_class))
        WebDriverWait(browser, 30).until(element_present)

        # 字典，存储获取过的内容
        span_class_dict = {}
        for replace_span_s in replace_content_s_list:
            cls = replace_span_s.attrs['class'][0]
            if cls not in span_class_dict:
                script = "return window.getComputedStyle(document.getElementsByClassName('%s')[0],'before').getPropertyValue('content')" % (
                cls)
                trans = browser.execute_script(script).strip('\"')
                span_class_dict[cls] = trans
            replace_span_s.replace_with(span_class_dict[cls])

        # 清除style和script
        [i.extract() for i in koubei_content.findAll('style')]
        [i.extract() for i in koubei_content.findAll('script')]

        item['content'] = koubei_content.get_text(strip=True)
        browser.quit()
        return item

