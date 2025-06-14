import re

from nonebot_plugin_alconna import Alconna, Args, on_alconna, At, UniMessage, Match
from nonebot_plugin_uninfo import Uninfo
from nonebot.plugin import PluginMetadata
from mengluo_vrc_bot.services.db import fetchone

from mengluo_vrc_bot.utils.rendering import *

AVATAR_ID_PATTERN = re.compile(r'^avtr_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
WORLD_ID_PATTERN = re.compile(r'^wrld_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
USER_ID_PATTERN = re.compile(r'^usr_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
GROUP_ID_PATTERN = re.compile(r'^grp_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')

__plugin_meta__ = PluginMetadata(
    name="信息获取",
    description="获取Vrchat信息",
    usage="""
    查看模型：查看模型信息，格式为avtr_前缀+UUID
    查看世界：查看世界信息，格式为wrld_前缀+UUID
    查看用户：查看用户信息，格式为usr_前缀+UUID，支持@用户
    我的vrc：查看当前绑定的VRC用户信息
    查看群组：查看群组信息，格式为grp_前缀+UUID
    """,
)

get_avatar = on_alconna(Alconna("查看模型", Args["id", str]), priority=5, block=True)
get_world = on_alconna(Alconna("查看世界", Args["id", str]), priority=5, block=True)
get_user = on_alconna(Alconna("查看用户", Args["id?", str, None]["at_user?", At]), priority=5, block=True)
my_info= on_alconna(Alconna("我的vrc"), aliases={"我的VRC"}, priority=5, block=True)
get_group = on_alconna(Alconna("查看群组", Args["id", str]), priority=5, block=True)
search_group = on_alconna(Alconna("搜索群组", Args["name", str]), priority=5, block=True)
search_user = on_alconna(Alconna("搜索用户", Args["name", str]), priority=5, block=True)
search_world = on_alconna(Alconna("搜索世界", Args["name", str]), priority=5, block=True)


@get_avatar.handle()
async def _(id: str):
    # 验证模型ID格式（avtr_前缀+UUID）
    if not AVATAR_ID_PATTERN.match(id):
        await get_avatar.finish("错误：模型ID格式不正确")
    img = await render_avatarinfo(id)
    if type(img) == str:
        await get_avatar.finish(img)
    await UniMessage.image(raw=img).send()


@get_world.handle()
async def _(id: str):
    # 验证世界ID格式（wrld_前缀+UUID）
    if not WORLD_ID_PATTERN.match(id):
        await get_world.finish("错误：世界ID格式不正确")
    img = await render_worldinfo(id)
    if type(img) == str:
        await get_world.finish(img)
    await UniMessage.image(raw=img).send()


@get_user.handle()
async def _(id: str| None, session: Uninfo, at_user: Match[At]):
    if at_user.available and session.group:
        user_id = at_user.result.target
        result = await fetchone("SELECT vrc_id FROM user_info WHERE user_id =?", user_id)
        if not result:
            await get_avatar.finish("错误：该用户未绑定vrc_id！")
        else:
            id = result[0]
    elif not USER_ID_PATTERN.match(id):
        await get_user.finish("错误：用户ID格式不正确")
    img = await render_userinfo(id)
    if type(img) == str:
        await get_user.finish(img)
    await UniMessage.image(raw=img).send()

@my_info.handle()
async def _(session: Uninfo):
    user_id = session.user.id
    result = await fetchone("SELECT vrc_id FROM user_info WHERE user_id =?", user_id)
    if not result:
        await my_info.finish("错误：您未绑定vrc_id！")
    else:
        id = result[0]
        img = await render_userinfo(id)
        if type(img) == str:
            await my_info.finish(img)
        await UniMessage.image(raw=img).send()

@get_group.handle()
async def _(id: str):
    # 验证群组ID格式（grp_前缀+UUID）
    if not GROUP_ID_PATTERN.match(id):
        await get_group.finish("错误：群组ID格式不正确")
    img = await render_groupinfo(id)
    if type(img) == str:
        await get_group.finish(img)
    await UniMessage.image(raw=img).send()


@search_group.handle()
async def _(name: str):
    await search_group.finish(f"你搜索的群组ID是: {name}")


@search_user.handle()
async def _(name: str):
    await search_user.finish(f"你搜索的用户ID是: {name}")


@search_world.handle()
async def _(name: str):
    await search_world.finish(f"你搜索的世界ID是: {name}")
