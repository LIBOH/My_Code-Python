import scrapy
import json
import re
from copy import deepcopy
from ..items import JdlingyuProjectItem


class JdlySpider(scrapy.Spider):
    name = 'jdly'
    allowed_domains = ['www.jdlingyu.com']
    start_urls = ['http://www.jdlingyu.com/']

    def parse(self, response):
        li_list = response.xpath('//*[@id="post-item-mzt"]/div[2]/ul/li')

        for li in li_list:
            detail_url = li.xpath('./div/div[1]/a/@href').get()
            yield scrapy.Request(detail_url, callback=self.detail_page)

        # 获取更多
        page = 2

        while True:
            end = input('-> 要额外获取的页数(输入"q"不获取更多)：')
            if end == 'q':
                break
            elif not end.isdigit():
                print('-> 请输入阿拉伯数字！')
                continue

            end = int(end)
            url = 'https://www.jdlingyu.com/wp-json/b2/v1/getModulePostList'
            for _ in range(end):
                data = {'index': '6', 'post_paged': str(page)}
                yield scrapy.FormRequest(url, formdata=data, callback=self.get_more)
                page += 1
            break

    def detail_page(self, response):
        item = JdlingyuProjectItem()
        item['title'] = response.xpath(
            '//*[@id="primary-home"]/article/header/h1//text()').get()

        img_list = response.xpath(
            '//*[@id="primary-home"]/article/div[2]/img/@src').getall()
        if img_list == []:
            img_list = response.xpath(
                '//*[@id="primary-home"]/article/div[2]/p/img/@src').getall()

        item['img_url_list'] = img_list
        yield deepcopy(item)

    def get_more(self, response):
        data = json.loads(response.text)['data']
        end_page = json.loads(response.text)['pages']

        url_list = re.findall(
            r'<h2><a  target="_blank" href="(.*?)">.*?</a></h2>', data)
        print(f'-----! 最大页数：{end_page} !-----')

        for url in url_list:
            yield scrapy.Request(url, callback=self.detail_page)
