from nonebot import on_regex
from typing import Annotated
from nonebot.params import RegexStr
from nonebot.plugin import PluginMetadata
from nonebot.adapters.onebot.v11 import MessageSegment

from mengluo_vrc_bot.utils.rendering import *

__plugin_meta__ = PluginMetadata(
    name="VRC链接解析",
    description="自动解析VRC链接并获取信息",
    usage="""
    发送VRC链接，机器人会自动解析并获取信息。
    """,
)

get_avatar = on_regex(r"avtr_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
get_world = on_regex(r"wrld_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
get_user = on_regex(r"usr_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")
get_group = on_regex(r"grp_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

@get_avatar.handle()
async def _(foo: Annotated[str, RegexStr()]):
    img = await render_avatarinfo(foo)
    if type(img) == str:
        await get_avatar.finish(img)
    await get_avatar.finish(MessageSegment.image(img))

@get_world.handle()
async def _(foo: Annotated[str, RegexStr()]):
    img = await render_worldinfo(foo)
    if type(img) == str:
        await get_world.finish(img)
    await get_world.finish(MessageSegment.image(img))

@get_user.handle()
async def _(foo: Annotated[str, RegexStr()]):
    img = await render_userinfo(foo)
    if type(img) == str:
        await get_user.finish(img)
    await get_user.finish(MessageSegment.image(img))

@get_group.handle()
async def _(foo: Annotated[str, RegexStr()]):
    img = await render_groupinfo(foo)
    if type(img) == str:
        await get_group.finish(img)
    await get_group.finish(MessageSegment.image(img))