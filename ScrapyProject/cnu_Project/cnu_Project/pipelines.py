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


class CnuProjectPipeline:
    def process_item(self, item, spider):
        # item['author'] = item['author'].strip()
        item['title'] = item['title'].strip()

        if item['title'] == '':
            none_title = 0
            item['title'] = f'无标题_{none_title}'
            none_title += 1

        item['title'] = item['title'].replace('/', '_')

        return item


class ImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        name = item['title']
        print(f'-> 开始下载-*- {name} -*-')
        for img_url in item['img_url_list']:
            yield scrapy.Request(img_url)

        return item

    def item_completed(self, results, item, info):
        image_path = [x["path"] for ok, x in results if ok]
        title = item['title']
        img_path = f'{IMAGES_STORE}/{title}'

        if os.path.exists(img_path) is False:
            os.mkdir(img_path)

        for name_count, path in enumerate(image_path):
            new_img_name = item['title'] + f'_{name_count}' + '.jpg'
            old_path = f'{IMAGES_STORE}/{path}'
            new_path = f'{IMAGES_STORE}/{title}/{new_img_name}'
            shutil.move(old_path, new_path)

        print(f'-> 已完成图集-[{title}]')
        return item
