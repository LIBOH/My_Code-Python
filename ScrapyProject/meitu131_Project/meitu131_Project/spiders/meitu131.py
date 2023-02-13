import scrapy
from ..items import Meitu131ProjectItem


class Meitu131Spider(scrapy.Spider):
    name = 'meitu131'
    allowed_domains = ['www.meitu131.com']
    start_urls = ['https://www.meitu131.com/meinv']

    def parse(self, response):
        li_list = response.xpath('/html/body/div[1]/div[2]/ul/li')
        for li in li_list:
            detail_url = f"https://www.meitu131.com{li.xpath('./div[1]/a/@href').get()}"
            print(f"一页共 {len(li_list)} 个 -- {detail_url}")
            yield scrapy.Request(detail_url, callback=self.detail_parse)

        # 翻页
        # 当前页面URL
        current_url = f'{response.request.url}'.split('/', 3)[-1]
        # 详细页面的最大URL
        end_img_url = response.xpath(
            '//*[@id="pages"]/a[last()]/@href').get().split('/', 1)[-1]
        # 下一页URL
        next_url = f'''https://www.meitu131.com{response.xpath('//*[@id="pages"]/a[last()-1]/@href').get()}'''

        if current_url != end_img_url:
            yield scrapy.Request(next_url, self.parse)

    def detail_parse(self, response):
        item = Meitu131ProjectItem()

        item['title'] = response.xpath(
            '//*[@id="main-wrapper"]/div[1]/h1').get().strip('</h1>')
        item['img_url'] = response.xpath(
            '//*[@id="main-wrapper"]/div[2]/p/a/img/@src').get()

        # 翻页
        # 当前页面URL
        current_url = f'{response.request.url}'.split('/', 3)[-1]
        # 详细页面的最大URL
        end_img_url = response.xpath(
            '//*[@id="pages"]/a[last()]/@href').get().split('/', 1)[-1]
        # 下一页URL
        next_url = f'''https://www.meitu131.com{response.xpath('//*[@id="pages"]/a[last()-1]/@href').get()}'''

        yield item
        if current_url != end_img_url:
            yield scrapy.Request(next_url, self.detail_parse)
