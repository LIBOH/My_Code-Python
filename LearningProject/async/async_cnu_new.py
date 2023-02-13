import os
import re
import json
import time
import shutil
import asyncio
from decimal import Decimal, ROUND_HALF_UP

import aiohttp
import aiofiles

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.47',
    'Referer': 'http://www.cnu.cc/'
}

if not os.path.exists('images/full/'):
    os.makedirs('images/full/')


async def get_data(url_):
    async with aiohttp.ClientSession() as session:
        async with session.get(url_, headers=headers) as resp:
            text = await resp.text()
            # 图片地址的json字符串
            rex_json = re.findall(
                r'<div id="imgs_json" style="display:none">(.*?)</div>', text)[0]
            json_str = json.loads(rex_json)

            # 图集标题
            rex_title = re.findall(
                r'<h2 class="work-title">(.*?)</h2>', text)[0].strip()

            return json_str, rex_title


async def downloader(img_url, title):
    global downloader_count
    downloader_count += 1

    suffix = img_url.rsplit('/')[-1].split('.')[-1]
    img_name = f'{title}_{downloader_count}.{suffix}'

    # 图片临时储存路径
    path = f'images/full/{img_name}'

    async with aiohttp.ClientSession() as session:
        async with session.get(img_url, headers=headers) as img_resp:
            content = await img_resp.read()

            async with aiofiles.open(path, 'wb') as f:
                await f.write(content)

    print('[Out]: 下载完成!')


def title_format(title) -> str:
    illegal_chars = ['<', '>', '?', '\\', '/', '|', '.', '*', '\u200b']
    if ' ' in title:
        title = title.replace(' ', '_')

    for char in illegal_chars:
        if char in title:
            title = title.replace(char, '')

    return title


def get_img_url(json_data) -> list:
    return ["http://imgoss.cnu.cc/" + data['img'] for data in json_data]


def move_img(title):
    """
        移动图片至新文件夹
    """
    print('[Out]: 正在移动图片至新目录...')
    files = os.listdir('images/full/')

    if not os.path.exists(f'images/{title}/'):
        os.makedirs(f'images/{title}/')

    for file in files:
        old_path = f'images/full/{file}'
        new_path = f'images/{title}/{file}'
        shutil.move(old_path, new_path)

    print('[Out]: 完成！')


def make_list_index(size):
    while True:
        page = input(
            f'[Out]: 您要下载第几张图片，不可超过_ {size} _, 直接回车以获取全部 (支持区间下载: 如 1--5 或 x<=3,x>=6): ')

        if page == '':
            return None, None

        elif page.isdigit():
            return int(page) - 1, int(page)

        if re.search(r'\d+--\d+', page):
            num = page.split('--')
            return int(num[0]) - 1, int(num[1])

        elif re.search(r'x<=\d+,x>=\d+', page):
            end_1 = page.split(',')[0].split('<=')[-1]
            start_2 = page.split(',')[-1].split('>=')[-1]
            return (None, int(end_1)), (int(start_2) - 1, None)

        print('[Out]: 您的命令有误，请重新输入！')


async def main(url_):
    start_time = time.time()

    json_data, title = await get_data(url_)
    img_url_list = get_img_url(json_data)
    format_title = title_format(title)

    print(
        f'[Out]:《{format_title}》_共 {len(img_url_list)} 张')

    start, end = make_list_index(len(img_url_list))
    if type(start) is tuple:
        tasks = [asyncio.create_task(downloader(img_url, format_title))
                 for img_url in img_url_list[start[0]:start[1]]]

    if type(end) is tuple:
        tasks = [asyncio.create_task(downloader(img_url, format_title))
                 for img_url in img_url_list[end[0]:end[-1]]]

    else:
        tasks = [asyncio.create_task(downloader(img_url, format_title))
                 for img_url in img_url_list[start:end]]

    await asyncio.wait(tasks)

    move_img(format_title)

    end_time = time.time() - start_time
    # 时间精确到小数点后两位
    finally_time = Decimal(str(end_time)).quantize(
        Decimal('0.00'), rounding=ROUND_HALF_UP)

    print(f'[Out]: 此次用时：{finally_time}秒\n')


if __name__ == '__main__':
    print('******************** 欢迎使用CNU图集获取程序 ********************')
    print('[Out]: CNU首页: http://www.cnu.cc/\n')

    while True:
        downloader_count = 0
        url = input('[In]: 请输入图集网址(输入<q>退出): ')
        print()
        if url in ['q', 'Q']:
            exit()
        elif 'http://www.cnu.cc/works/' not in url:
            print('[Out] 请输入一个 CNU图集 网址！\n')
            continue

        asyncio.run(main(url))
