from nonebot_plugin_alconna import Alconna, Args, on_alconna, UniMessage

from .rendering import *

get_avatar = on_alconna(Alconna("查看模型", Args["id", str]))
get_world = on_alconna(Alconna("查看世界", Args["id", str]))
get_user = on_alconna(Alconna("查看用户", Args["id", str]))
get_group = on_alconna(Alconna("查看群组", Args["id", str]))
search_group = on_alconna(Alconna("搜索群组", Args["name", str]))
search_user = on_alconna(Alconna("搜索用户", Args["name", str]))
search_world = on_alconna(Alconna("搜索世界", Args["name", str]))


@get_avatar.handle()
async def _(id: str):
    # 验证模型ID格式（avtr_前缀+UUID）
    if not re.match(r'^avtr_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', id):
        await get_avatar.finish("错误：模型ID格式不正确，示例：avtr_d519f3d1-122c-423c-a355-ca453a6513e2")
    img = await render_avatarinfo(id)
    if type(img) == str:
        await get_avatar.finish(img)
    await UniMessage.image(raw=img).send()


@get_world.handle()
async def _(id: str):
    # 验证世界ID格式（wrld_前缀+UUID）
    if not re.match(r'^wrld_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', id):
        await get_world.finish("错误：世界ID格式不正确，示例：wrld_c16e4dee-d149-4116-adbc-16bc30b664b0")
    img = await render_worldinfo(id)
    if type(img) == str:
        await get_world.finish(img)
    await UniMessage.image(raw=img).send()


@get_user.handle()
async def _(id: str):
    # 验证用户ID格式（usr_前缀+UUID）
    if not re.match(r'^usr_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', id):
        await get_user.finish("错误：用户ID格式不正确，示例：usr_cec4a881-191f-4834-b440-e66ecc937a57")
    img = await render_userinfo(id)
    if type(img) == str:
        await get_user.finish(img)
    await UniMessage.image(raw=img).send()


@get_group.handle()
async def _(id: str):
    # 验证群组ID格式（grp_前缀+UUID）
    if not re.match(r'^grp_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$', id):
        await get_group.finish("错误：群组ID格式不正确，示例：grp_ef4bf571-8b5e-4068-b503-49a9a52829cf")
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
