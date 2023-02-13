# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import shutil
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from .settings import IMAGES_STORE


class JdlingyuProjectPipeline:
    def process_item(self, item, spider):
        return item


class imagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        print('-> 图片下载中...')
        for img_url in item['img_url_list']:
            yield scrapy.Request(img_url)
        return item

    def item_completed(self, results, item, info):
        image_path = [x["path"] for ok, x in results if ok]
        title = item['title']
        img_path = f'{IMAGES_STORE}/{title}'

        if os.path.exists(img_path) is False:
            os.mkdir(img_path)

        for path in image_path:
            old_path = f'{IMAGES_STORE}/{path}'
            new_path = f'{IMAGES_STORE}/{title}/' + path.split('/')[-1]
            shutil.move(old_path, new_path)

        print('-> 完成！')
        return item
