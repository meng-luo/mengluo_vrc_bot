from nonebot_plugin_alconna import Alconna, Args, UniMessage, on_alconna
from nonebot_plugin_uninfo import Uninfo
from nonebot.adapters import Bot

from mengluo_vrc_bot.utils.rendering import render_friendsinfo

online_friends = on_alconna(Alconna("在线好友", Args["number", int, 50]))

@online_friends.handle()
async def _(bot: Bot, session: Uninfo, number: int):
    if session.user.id in bot.config.superusers:
        if number > 100:
            await online_friends.finish("最多只能查询100个好友")
        img = await render_friendsinfo(False, number)
        if type(img) == str:
            await online_friends.finish(img)
        await UniMessage.image(raw=img).send()
    else:
        await online_friends.finish("需要登录VRC账号才能使用该功能") # 画饼（bushi