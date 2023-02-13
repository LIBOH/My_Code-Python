import json
import os

import aiofiles
from nonebot import get_driver
from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageSegment
from lxml import etree
from httpx import AsyncClient, Response

from .config import plugin_config
from .utils import *


async def get_handpick():
    """
    请求 CNU首页 获取当下最新的两个每日精选图集
    :return:
    """
    saved_file = await load_file()
    try:
        with open(f'{plugin_config["cnu_data_path"]}{saved_file}', 'r', encoding='utf-8') as f:
            file_content = json.loads(f.read())
            content = file_content['content']
            # 创建回复用的信息 Message
            nickname = list(get_driver().config.nickname)[0]
            return [
                f'哈喽{MessageSegment.face(66)} 今天是{get_iso_weekday()}{MessageSegment.face(183)}~\n',
                f'{nickname}给您送上新鲜出炉的每日精选图集啦~\n\n',
                f'日期：{file_content["send_date"]}\n',
                f'标题：{content[0]["title"]}\n',
                f'作者：{content[0]["author"]}\n',
                f'标签：{content[0]["tag"]}\n',
                MessageSegment.image(content[0]["thumbnail"]),
                f'网址：{content[0]["atlas_url"]}\n\n',
                f'标题：{content[1]["title"]}\n',
                f'作者：{content[1]["author"]}\n',
                f'标签：{content[1]["tag"]}\n',
                MessageSegment.image(content[1]["thumbnail"]),
                f'网址：{content[1]["atlas_url"]}']

    except FileNotFoundError as e:
        logger.error('获取每日精选失败，数据文件已丢失或不存在.')
        return 'oops~  每日精选获取失败'


async def async_get_response(client: AsyncClient, url_: str, headers: dict):
    """
    向目标网址发起请求 返回该页面的 Response对象
    :param client: httpx.AsyncClient()对象
    :param url_: 目标网址
    :param headers: 请求头
    :return: 目标网址的 Response对象
    """
    try:
        res = await client.get(url_, headers=headers, timeout=60)
        return res
    except Exception as e:
        logger.error('网页链接超时.')


async def get_newly_handpick_time(response: Response):
    """
    获取最新的每日精选发布时间
    :param response: 网站页面的网络响应对象
    :return: 每日精选最新发布时间
    """
    html_obj = etree.HTML(response.text)
    t = html_obj.xpath(f'//ul[@id="selected"]/div[1]/text()')[0]
    logger.info(f'获取到最新发布时间为: {t}')
    return t


async def get_handpick_from_internet(response: Response) -> None:
    """
    从网站上获取最新一期的每日精选
    :param response: 网站页面的网络响应对象
    :return: None
    """
    logger.info('正在提取最新数据...')
    html_obj = etree.HTML(response.text)
    send_date = await get_newly_handpick_time(response)

    data = {
        'send_timestamp': int(time.mktime(time.strptime(send_date, '%Y-%m-%d'))),
        'send_date': send_date,
        'content': [],
        'cnu_data_path': ''
    }

    for i in range(1, 3):
        content = {
            'title': title_format(html_obj.xpath(f'//ul[@id="selected"]/li[{i}]/div/a/h3/text()')[0]),
            'tag': html_obj.xpath(f'//ul[@id="selected"]/li[{i}]/div/span/text()')[0].strip(),
            'atlas_url': html_obj.xpath(f'//ul[@id="selected"]/li[{i}]/div/a/@href')[0],
            'author': html_obj.xpath(f'//ul[@id="selected"]/li[{i}]/div/div[2]/a/text()')[1].strip(),
            'thumbnail': html_obj.xpath(f'//ul[@id="selected"]/li[{i}]/a/img/@src')[0]
        }
        data['cnu_data_path'] = f"{plugin_config['cnu_data_path']}{data['send_date']}_每日精选.json"
        data['content'].append(content)

    logger.info(f'提取到的数据 | {data}')
    logger.info('提取完成, 即将开始保存json文件')
    await update_file(data)


async def update_file(data) -> None:
    """
    将最新的每日精选内容写入 json文件
    :param data: 最新一期每日精选的数据内容
    :return: None
    """
    for _, _, files in os.walk(plugin_config['cnu_data_path']):
        if files:
            logger.info(f"正在删除文件: {files[0]}")
            os.remove(f"{plugin_config['cnu_data_path']}{files[0]}")

    async with aiofiles.open(f'{plugin_config["cnu_data_path"]}{data["send_date"]}_每日精选.json', 'w',
                             encoding='utf-8') as f:
        await f.write(json.dumps(data))
        logger.info(f'{plugin_config["cnu_data_path"]}{data["send_date"]}_每日精选.json 保存成功!')


async def load_file():
    """
    获取最新的json文件
    :return: 文件名 -> yyyy-mm-dd_每日精选.json
    """
    for _, _, files in os.walk(plugin_config['cnu_data_path']):
        if files:
            logger.info(f'当前已保存的最新数据文件: {files[0]}')
            return files[0]
        else:
            return '0001-01-01_每日精选.json'

