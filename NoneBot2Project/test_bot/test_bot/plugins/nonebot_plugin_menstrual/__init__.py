from nonebot.matcher import Matcher
from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import Arg, CommandArg

from .menstrual_assistant import MenstrualDate

names = ('资明辕',)
ms = on_command('经期', priority=10)


@ms.handle()
async def ms(matcher: Matcher, name: Message = CommandArg()):
    name_str = name.extract_plain_text()
    if name_str and name_str in names:
        matcher.set_arg("name", name)
        await matcher.finish(MenstrualDate(2022, 11, 4, 26).__str__())
    await matcher.reject(name.template('查询的用户不存在！请重新输入...'))

# @ms.got('name', prompt='要查询谁的经期？')
# async def handle_name(matcher: Matcher, name: Message = Arg()):
#     if name not in names:
#         await ms.reject(name.template('查询的用户不存在！请重新输入...'))
#
#     await matcher.finish(MenstrualDate(2022, 11, 4, 26).__str__())
