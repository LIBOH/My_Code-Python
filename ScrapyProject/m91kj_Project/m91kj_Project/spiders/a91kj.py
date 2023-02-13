import scrapy
from ..items import M91KjProjectItem
from copy import deepcopy

start_page = input('你要开始获取的页数：')
end_page = input('结束的页数(回车则为末页)：')


class A91kjSpider(scrapy.Spider):
    name = '91kj'
    allowed_domains = ['www.91kanju2.com']
    start_urls = [f'https://www.91kanju2.com/vod-show/8/{start_page}.html']

    def parse(self, response):
        global start_page
        item = M91KjProjectItem()

        li_list = response.xpath('/html/body/div[2]/div/div/div/div[3]/ul/li')
        for li in li_list:
            item['Detail_url'] = 'https://www.91kanju2.com' + \
                li.xpath('./div/a/@href').get()

            yield scrapy.Request(item['Detail_url'], callback=self.get_detail, meta={'item': deepcopy(item)})

        # 下一页
        this_url = f'vod-show/8/{start_page}.html'
        start_page = int(start_page) + 1
        next_url = f'https://www.91kanju2.com/vod-show/8/{start_page}.html'
        if end_page is None:
            if int(start_page) > 4:
                end_url = response.xpath(
                    '/html/body/div[2]/div/ul/li[14]/a/@href').get()
            else:
                end_url = response.xpath(
                    '/html/body/div[2]/div/ul/li[13]/a/@href').get()
        else:
            end_url = f'vod-show/8/{end_page}.html'
        if this_url != end_url:
            yield scrapy.Request(next_url, callback=self.parse)

    def get_detail(self, response):
        item = response.meta['item']
        item['Title'] = response.xpath(
            '/html/body/div[2]/div/div[1]/div/div/div[1]/div/div[2]/h3/span[1]/text()').get()
        item['Score'] = response.xpath(
            '/html/body/div[2]/div/div[1]/div/div/div[1]/div/div[2]/h3/span[2]/text()').get()

        a_info = response.xpath(
            '/html/body/div[2]/div/div[1]/div/div/div[1]/div/div[2]/p[3]//a/text()').getall()
        if a_info[-1].isdigit():
            item['Year'] = a_info[-1]

        try:
            if a_info[-2] in ['大陆', '内地']:
                item['Region'] = a_info[-2].replace(
                    '大陆', '中国大陆') or a_info[-2].replace('内地', '中国大陆')
            else:
                item['Region'] = a_info[-2]

        except IndexError:
            item['Region'] = '未知'

        finally:
            try:
                item['Type'] = a_info[:-2][0].strip()
            except IndexError:
                item['Type'] = '未知'
            finally:
                yield deepcopy(item)
