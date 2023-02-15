from nonebot.matcher import Matcher
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg
from nonebot.log import logger

from .utils import init_data, modify_data
from .menstrual import *


init_ms = on_command('init', aliases={'初始化'}, priority=10)
ms = on_command('ms', priority=10)
update = on_command('update', priority=10)


@init_ms.handle()
async def init_menstrual(matcher: Matcher, user_data: Message = CommandArg()):
    if data := user_data.extract_plain_text():
        try:
            data_list = data.split(' ')
            if '' in data_list:
                await matcher.finish('请确认命令末尾不能含有空格!')

            init_data(*data.split(' '))
            await matcher.finish('用户数据初始化完成!')

        except TypeError as e:
            logger.warning(e)
            await matcher.finish('参数错误或不完整, 请重新输入...\n示例命令: 初始化 张三 2023-01-01 28 3')


@ms.handle()
async def info(matcher: Matcher, commands: Message = CommandArg()):
    if command := commands.extract_plain_text():
        command_list = command.split(' ')
        if len(command_list) != 2:
            logger.warning('参数不完整或出错!')
            return

        command_type, name = command_list
        match command_type:
            case '总览':
                await matcher.finish(total_info(name))

            case '删除':
                delete_data(name)
                await matcher.finish(f'<{name}>用户数据已删除!')


@update.handle()
async def update_filed(matcher: Matcher, commands: Message = CommandArg()):
    if command := commands.extract_plain_text():
        command_list = command.split(' ')
        if len(command_list) != 3:
            return

        keymap = {
            '上次开始': 'pred_start',
            '上次结束': 'pred_end',
            '上次月经天数': 'pred_duration',
            '默认月经天数': 'duration',
            '下次开始': 'next_start',
            '提前提醒': 'advance_prompt',
            '月经周期': 'cycle',
        }

        name, key, value = command_list
        modify_data(name, keymap[key], value)
        logger.info(f'key<{key}-{keymap[key]}>的值已修改为<{value}>')

        await matcher.finish(f'<{name}>的<{key}>已修改为<{value}>')
