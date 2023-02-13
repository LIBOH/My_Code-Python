import os

from pydantic import BaseModel, Extra
from nonebot import get_driver
from nonebot.log import logger

default_cnu_img_path = './data/nonebot_plugin_cnu/images/'     # 机器人文件夹中的相对路径
default_data_path = './data/nonebot_plugin_cnu/data/'               # 机器人文件夹中的相对路径


class Config(BaseModel, extra=Extra.ignore):
    cnu_img_path: str
    cnu_data_path: str
    cnu_private_friends: list
    cnu_groups: list
    cnu_inform_time: dict


def check_path(config: dict, field: str):
    """
    check and set default path
    :param config: 读取的.env配置文件
    :param field: 本插件配置的字段
    :return:
    """
    if field == 'cnu_img_path':
        if not config[field]:
            logger.info(f'未检测到图片保存路径，将使用默认路径"{default_cnu_img_path}"')
            config[field] = default_cnu_img_path
        make_dir(plugin_config['cnu_img_path'])

    elif field == 'cnu_data_path':
        if not config[field]:
            logger.info(f'未检测到data储存路径，将使用默认路径"{default_cnu_img_path}"')
            config[field] = default_data_path
        make_dir(plugin_config['cnu_data_path'])


def make_dir(path):
    if not os.path.exists(path):
        logger.info(f'file: {__name__}  | func: "make_dir" | 文件夹不存在, 即将创建文件夹...')
        os.makedirs(path)
        logger.info(f'file: {__name__} | func: "make_dir" | 创建完成!')
    logger.info(f'file: {__name__} | func: "make_dir" | 文件夹已存在, 跳过创建.')


plugin_config = Config.parse_obj(get_driver().config).dict()
check_path(plugin_config, 'cnu_img_path')
check_path(plugin_config, 'cnu_data_path')
