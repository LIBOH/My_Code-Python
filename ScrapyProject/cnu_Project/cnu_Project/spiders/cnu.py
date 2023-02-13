import json
import scrapy
from ..items import CnuProjectItem


class CunSpider(scrapy.Spider):
    while True:
        start_count = input('请选择开始获取的页数：')
        max_page = input('您要获取的最大页数：')
        if start_count.isdigit() is False or max_page.isdigit() is False:
            print('-> 请输入一个整数！')
            continue
        else:
            break

    name = 'cnu'
    allowed_domains = ['www.cnu.cc']
    start_urls = [
        'http://www.cnu.cc/discoveryPage/recent-0?page=' + start_count]

    def parse(self, response):
        div_list = response.xpath('//*[@id="recommendForm"]/div/div')

        for div in div_list[2:]:
            detail_url = div.xpath('./a/@href').get()

            yield scrapy.Request(detail_url, callback=self.get_detail)

        # 翻页
        page_count = 2
        next_page = f'http://www.cnu.cc/discoveryPage/recent-0?page={self.max_page}'
        if page_count <= int(self.max_page):
            yield scrapy.Request(next_page, callback=self.parse)
            page_count += 1

    def get_detail(self, response):
        item = CnuProjectItem()

        item['title'] = response.xpath(
            '/html/body/div[1]/div[2]/h2/text()').get()
        # 作者
        item['author'] = response.xpath(
            '/html/body/div[1]/div[2]/span/a/strong/text()').get()

        json_data = json.loads(response.xpath(
            '//*[@id="imgs_json"]/text()').get())

        img_url_list = []
        for data in json_data:
            img_url = 'http://imgoss.cnu.cc/' + data['img']
            img_url_list.append(img_url)

        item['img_url_list'] = img_url_list

        # yield item

        # 过滤内容
        if item['author'] != ' 张三的自我画像':
            yield item
