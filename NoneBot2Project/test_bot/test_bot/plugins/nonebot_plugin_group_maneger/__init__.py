from nonebot import on_request
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import FriendRequestEvent, Bot, GroupRequestEvent


request = on_request(priority=5)


@request.handle()
async def _(bot: Bot, event: FriendRequestEvent):
    """加好友申请 自动同意"""
    if event.post_type == 'request':
        logger.info(f"接收到用户为: {event.user_id}的好友申请。")
        flag = event.flag
        await bot.set_friend_add_request(flag=flag, approve=True)


@request.handle()
async def _(bot: Bot, event: GroupRequestEvent):
    """加群申请 自动同意"""
    if event.post_type == 'request':
        logger.info(f"接收到用户为: {event.user_id}的加群({event.group_id})申请。")
        flag = event.flag
        sub_type = event.sub_type

        await bot.set_group_add_request(flag=flag, sub_type=sub_type, approve=True)


