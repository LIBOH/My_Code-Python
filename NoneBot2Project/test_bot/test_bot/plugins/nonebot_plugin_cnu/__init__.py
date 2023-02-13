from nonebot_plugin_apscheduler import scheduler
from nonebot.matcher import Matcher

from nonebot import on_command, require, get_bot
from nonebot.adapters.cqhttp import Message
from nonebot.log import logger

from .handpick import *
from .config import plugin_config
from .utils import *

require("nonebot_plugin_apscheduler")

cnu_command = on_command('cnu', priority=5)
cnu_update = on_command('cnu update', aliases={'cnu更新数据'}, priority=5)

friend_list = plugin_config['cnu_private_friends']
group_list = plugin_config['cnu_groups']


@cnu_command.handle()
async def show_handpick(matcher: Matcher):
    msg = await get_handpick()
    await matcher.send(message=Message(msg))


trigger = plugin_config['cnu_inform_time']['trigger']
hour = plugin_config['cnu_inform_time']['hour']
minute = plugin_config['cnu_inform_time']['minute']


# 定时任务: 发送每日精选
@scheduler.scheduled_job(trigger=trigger, hour=hour, minute=minute)
async def timing_handpick():
    logger.info("开始执行定时任务 | func: 'timing_handpick'")
    msg = Message(await get_handpick())

    try:
        for qq in friend_list:
            await get_bot().call_api("send_private_msg", user_id=qq, message=msg)
        for group in group_list:
            await get_bot().call_api("send_group_msg", group_id=group, message=msg)
    except TypeError:
        logger.error("插件定时发送相关设置有误，请检查.env.*文件。")
    finally:
        logger.info("定时任务执行完成 | func: 'timing_handpick'")


# 定时任务: 获取最新数据
@cnu_update.handle()
@scheduler.scheduled_job(trigger='cron', hour='12', minute='30')
async def timing_get_data():
    logger.info("开始执行定时任务 | func: 'timing_get_data'")

    url = 'http://www.cnu.cc/selectedPage'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'Referer': 'http://www.cnu.cc/selectedPage'
    }

    # 查看已保存的最新每日精选数据
    local_file = await load_file()
    # 将 '_'前面的日期分割出来 并 使用分割的日期创建date对象
    local_date = get_date(local_file.split('_')[0])

    async with AsyncClient() as client:
        # 获取网页响应对象
        res = await async_get_response(client, url, headers)
        # 获取最新一期每日精选的日期
        online_file = await get_newly_handpick_time(res)
        # 创建获取到的最新日期的date对象
        online_date = get_date(online_file)

        # 判断 已保存的日期 是否小于 最新日期. 如果False: 则获取最新数据并保存为本地json文件
        if local_date.__lt__(online_date):
            logger.info('网站数据已更新, 即将获取最新数据.')
            await get_handpick_from_internet(res)
        else:
            logger.info('网站数据未更新, 继续使用本地数据.')

        try:
            for qq in friend_list:
                await get_bot().call_api("send_private_msg", user_id=qq, message='数据更新成功！')
            for group in group_list:
                await get_bot().call_api("send_group_msg", group_id=group, message='数据更新成功！')
        except TypeError:
            logger.error("插件定时发送相关设置有误，请检查.env.*文件。")
        finally:
            logger.info("定时任务执行完成 | func: 'timing_get_data'")
