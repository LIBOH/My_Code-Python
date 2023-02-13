# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import csv

title = ['Title', 'Score', 'Type', 'Region', 'Year', 'Detail_url']


class M91KjProjectPipeline:
    def open_spider(self, spider):
        self.f = open('91看剧.csv', mode='a', encoding='utf-8', newline='')
        self.writer = csv.DictWriter(self.f, fieldnames=title)
        self.writer.writeheader()
        print('-> 开始写入文件!')

    def close_spider(self, spider):
        self.f.close()
        print('-> 写入完毕!')

    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item
