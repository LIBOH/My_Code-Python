from nonebot import on_command

command = on_command('help', aliases={'帮助'}, priority=10)

__help__ = """------------- 指令 -------------
CNU cnu -> 查看CNU每日精选  (CNU) (cnu)
lc每日 -> 查询每日一题  (lc每日)
lc查找 -> 搜索题目  (lc查找)
lc随机 -> 随机一题  (lc随机)
lc查询 -> 查询用户信息  (lc查询)
.help -> 查看疫情相关指令  (.help)
"""


@command.handle()
async def _():
    await command.send(__help__)
