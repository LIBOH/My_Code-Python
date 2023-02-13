import asyncio
import json
import os
import shutil
import time
from copy import deepcopy

import aiofiles
import aiohttp
import requests
from lxml import etree


class Crawler:
    def __init__(self):
        self._OK = 200
        self._EMPTY_WORKS_STATU_CODE = 0
        self._empty_atlas = {
            'statu_code': self._EMPTY_WORKS_STATU_CODE,
            'content': {
                'images_url': [],
                'atlas_title': '',
                'auther': '',
                'auther_href': '',
                'recommend_count': '',
                'read_count': '',
                'release_date': ''
            },
        }
        self.complete_time = None
        self.cus_path = None
        self.preview_status_code = None
        self.download_path = None
        self.folder_count = 1

        self.CACHE_DEFAULT_PATH = None
        self.WORKS_DEFAULT_DIR_PATH = None
        self.WORKS_DEFAULT_FULL_PATH = None

        self._HEADERS = {
            'Host': 'www.cnu.cc',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/103.0.5060.53 Safari/537.36 Edg/103.0.1264.37'
        }

    @staticmethod
    def _format_title(atlas_title: str) -> str:
        illegal_chars = ['\\', '/', '|', '.', ':', '<', '>', '?', '*', '\u200b']
        atlas_title = atlas_title.strip()
        if ' ' in atlas_title:
            atlas_title = atlas_title.replace(' ', '_')

        for char in illegal_chars:
            if char in atlas_title:
                atlas_title = atlas_title.replace(char, '')
        return atlas_title

    @staticmethod
    def _format_auther_info(info: list[str]):
        data = [i.strip() for i in info[:-1]]
        date = data.pop().split(' ')[0]
        auther = ''.join(data)

        return auther, date

    def make_dir(self):
        if not os.path.exists(self.CACHE_DEFAULT_PATH):
            os.makedirs(self.CACHE_DEFAULT_PATH)
        if not os.path.exists(self.WORKS_DEFAULT_FULL_PATH):
            os.makedirs(self.WORKS_DEFAULT_FULL_PATH)

    def get_atlas(self, works_url: str) -> str:
        with requests.get(works_url, headers=self._HEADERS) as res:
            if res.status_code != 200:
                self._empty_atlas['statu_code'] = res.status_code
                return json.dumps(self._empty_atlas)

            html_obj = etree.HTML(res.text)

            rex_json = json.loads(html_obj.xpath('//*[@id="imgs_json"]/text()')[0])
            auther_href = html_obj.xpath('/html/body/div[1]/div[2]/span/a/@href')[0]
            atlas_title = html_obj.xpath('/html/body/div[1]/div[2]/h2/text()')[0].strip()
            info_auther = html_obj.xpath('//span[@class="author-info"]//text()')
            recommend_count = html_obj.xpath('//span[@id="recommend_count"]/text()')[0].split(': ')[-1]
            read_count = html_obj.xpath('//div[@class="category"]/span[2]/span/text()')[0]
            info_data = self._format_auther_info(info_auther)
            atlas_title = self._format_title(atlas_title)

            resule_atlas = deepcopy(self._empty_atlas)
            resule_atlas['statu_code'] = res.status_code
            resule_atlas['content']['images_url'] = rex_json
            resule_atlas['content']['atlas_title'] = atlas_title
            resule_atlas['content']['auther'] = info_data[0]
            resule_atlas['content']['auther_href'] = f'{auther_href}?page=1'
            resule_atlas['content']['recommend_count'] = recommend_count
            resule_atlas['content']['read_count'] = read_count
            resule_atlas['content']['release_date'] = info_data[-1]

            return json.dumps(resule_atlas)

    def get_works(self, auther_href) -> str:
        with requests.get(auther_href, headers=self._HEADERS) as res:
            html_obj = etree.HTML(res.text)

            div_list = html_obj.xpath('//*[@id="recommendForm"]/div')
            content = [{
                'autherName': html_obj.xpath('/html/body/div[1]/div[2]/div/div[1]/span[1]/text()')[0],
                'content': {
                    'atlas_url': f"{div.xpath('./a/@href')[0]}",  # 图集网址,
                    'thumbnail_url': div.xpath('./a/img/@src')[0].split('?')[0],  # 缩略图 url,
                    'release_time': div.xpath('./a/div[2]/text()')[0].strip(),  # 图集发布时间
                    'atlas_title': div.xpath('./a/div[1]/text()')[0].strip(),  # 图集标题
                }
            }for div in div_list]

            return json.dumps(content)

    def atlas_preview(self, image_url: str):
        cache_name = image_url.rsplit('.', 1)[0].rsplit('/', 1)[1]
        try:
            with open(f"{self.CACHE_DEFAULT_PATH}/{cache_name}", 'rb') as f:
                length = os.path.getsize(f"{self.CACHE_DEFAULT_PATH}/{cache_name}")
                image_data = f.read(length)

            if b'<!doctype html>' in image_data:
                if self.preview_status_code:
                    return self.preview_status_code, None
                else:
                    return self._EMPTY_WORKS_STATU_CODE, None

            return self._OK, image_data

        except IOError:
            print("没有缓存, 开始下载缓存...")
            with requests.get(image_url) as res:
                self.preview_status_code = res.status_code
                with open(f"{self.CACHE_DEFAULT_PATH}/{cache_name}", 'wb') as f:
                    f.write(res.content)
            return self.atlas_preview(image_url)

    def _move_folder(self, old_path, new_path) -> None:
        path = f"{new_path}/{old_path.rsplit('/', 1)[-1]}"
        try:
            if os.path.exists(path):
                return self._extracted_from_move_folder(old_path, new_path)
            self.folder_count = 1
            shutil.move(old_path, new_path)

        except Exception as e:
            print(f'Spider._move_folder: {e}')

    # TODO Rename this here and in `_move_folder`
    def _extracted_from_move_folder(self, old_path, new_path):
        folder_name = old_path.rsplit(' ', 1)[0]
        folder_suffix = f"({self.folder_count})"
        new_name = f"{folder_name} {folder_suffix}"

        os.rename(old_path, new_name)
        self.folder_count += 1
        return self._move_folder(new_name, new_path)

    async def _downloader(self, image_url: str, count: int, works_title: str) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as res:
                content = await res.read()

                async with aiofiles.open(f"{self.download_path}/{works_title}_{count}.jpg", 'wb') as f:
                    await f.write(content)

    async def start_downloader(self, atlas, download_indexes, cus_path) -> None:
        atlas_title = atlas.atlas_title

        # 创建 默认 下载文件夹  default
        self.download_path = f"{self.WORKS_DEFAULT_FULL_PATH}/{atlas_title}"
        if not os.path.exists(self.download_path):
            os.mkdir(f"{self.download_path}")

        start_time = time.time()

        tasks = [asyncio.create_task(
            self._downloader(
                atlas.images_url[i],
                i + 1,
                atlas_title
            )) for i in download_indexes]
        await asyncio.wait(tasks)

        self._move_folder(f'{self.download_path}', f'{cus_path}')
        self.complete_time = round(time.time() - start_time, 2)
