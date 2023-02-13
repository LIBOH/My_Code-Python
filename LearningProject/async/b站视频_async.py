import asyncio
import os
import re
import time
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP

import aiofiles
import aiohttp
from lxml import etree

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.54',
    "referer": "https://www.bilibili.com/",
    "cookie": "i-wanna-go-back=-1; buvid3=62C0478D-55C8-A0E4-E581-0C2DEA2F7F6050219infoc; _uuid=16A106437-EE102-B6B5-4DBB-B9D63D45E6E950700infoc; buvid4=15836BC9-725B-E743-4EA0-45CA2875C4E451257-022042000-OW+LujapGXYMwXkgyyoPOQ%3D%3D; buvid_fp_plain=undefined; LIVE_BUVID=AUTO9716503855377441; CURRENT_BLACKGAP=0; rpdid=|(JJmYYJmlm|0J'uYl|RlJYkk; nostalgia_conf=-1; CURRENT_QUALITY=116; hit-dyn-v2=1; fingerprint=05c9341784658ae39dbbf5818cfa0d79; DedeUserID=172563311; DedeUserID__ckMd5=006eb3a788caf8c5; buvid_fp=05c9341784658ae39dbbf5818cfa0d79; b_ut=5; blackside_state=0; SESSDATA=bfac0c18%2C1675934086%2Ca2295%2A81; bili_jct=0b1f64c3b5939cd96b7b5cd2d3e71d2d; b_lsid=58F821E8_1829D1DF5E1; sid=6xss1h0o; b_timer=%7B%22ffp%22%3A%7B%22333.1007.fp.risk_62C0478D%22%3A%221829D1DF94C%22%2C%22333.788.fp.risk_62C0478D%22%3A%221829D1E20EA%22%7D%7D; theme_style=light; CURRENT_FNVAL=4048; PVID=2; innersign=0"
}

if not os.path.exists('B站视频合成/'):
    os.mkdir('B站视频合成/')


async def get_data(_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(_url, headers=headers) as resp:
            text = await resp.text()
            html_obj = etree.HTML(text)

            # 提取视频标题
            title = html_obj.xpath('//title/text()')[0]
            title = title.split('_')[0]
            print(f">>> {title}")

            # 提取视频、音频
            url_str = html_obj.xpath(
                '//script[contains(text(),"window.__playinfo__")]/text()')[0]
            video_url = re.findall(
                r'"video":\[{"id":\d+,"baseUrl":"(.*?)"', url_str)[0]
            audio_url = re.findall(
                r'"audio":\[{"id":\d+,"baseUrl":"(.*?)"', url_str)[0]

    return title, video_url, audio_url


async def media_downloader(title, media_url, base_url, count):
    global headers
    suffix = ['mp4', 'mp3']

    local_headers = deepcopy(headers)
    local_headers['referer'] = base_url

    async with aiohttp.ClientSession() as session:
        async with session.get(media_url, headers=local_headers) as resp:
            content = await resp.read()

            print(f'>>> 正在下载{suffix[count]}文件...')
            async with aiofiles.open(f'B站视频合成/{title}_engineering.{suffix[count]}', 'wb') as f:
                await f.write(content)


def title_format(title):
    illegal_chars = ['\\', '/', '|', '.']
    if ' ' in title:
        title = title.replace(' ', '_')

    for char in illegal_chars:
        if char in title:
            title = title.replace(char, '')

    return title


def video_synthesis(title):
    """将视频、音频合成 并 删除纯视频纯音频"""
    print('>>> 视频合成中....')
    os.system(
        f'ffmpeg -loglevel quiet \
            -i "B站视频合成/{title}_engineering.mp4" \
            -i "B站视频合成/{title}_engineering.mp3" \
            -c copy "B站视频合成/{title}.mp4"'
    )

    os.remove(f'B站视频合成/{title}_engineering.mp3')
    os.remove(f'B站视频合成/{title}_engineering.mp4')

    print('>>> 完成!已删除纯视频、纯音频。\n' + '-' * 30)


async def main(url):
    start_time = time.time()

    media_tuple = await get_data(url)

    # 格式化标题
    format_title = title_format(media_tuple[0])

    tasks = [asyncio.create_task(media_downloader(format_title, media_url, url, count)) for count, media_url in
             enumerate(media_tuple[1:])]
    await asyncio.wait(tasks)

    # ffmpeg合成视频
    video_synthesis(format_title)

    end_time = time.time() - start_time
    # 时间精确到小数点后两位
    spend_time = Decimal(str(end_time)).quantize(
        Decimal('0.00'),
        rounding=ROUND_HALF_UP
    )

    print(f'>>> 此次用时：{spend_time}秒\n')


if __name__ == '__main__':
    while True:
        url = input('>>> 请输入目标视频的网址(输入q退出): \n')
        if url in ['q', 'Q']:
            exit()
        elif 'https://www.bilibili.com/video/' not in url:
            print('>>> 请输入一个视频播放页面的网址！')
            continue

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main(url))
