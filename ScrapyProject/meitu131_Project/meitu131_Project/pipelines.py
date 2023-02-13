# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import os
import shutil

import scrapy
from .settings import IMAGES_STORE
from scrapy.pipelines.images import ImagesPipeline


class Meitu131ProjectPipeline:
    def process_item(self, item, spider):
        return item


class imagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        title = item['title'].split(' ')
        img_name = f'{title[1]}_{title[-1]}.jpg'
         
        yield scrapy.Request(item['img_url'], meta={'name': img_name, 'dir_name': title[0]})
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return f"{request.meta['dir_name']}/{request.meta['name']}"

    def item_completed(self, results, item, info):

        old_path = [x["path"] for ok, x in results if ok]

        print(f"{old_path[0].rsplit('/')[-1]} -- 下载完成！")
        return item
