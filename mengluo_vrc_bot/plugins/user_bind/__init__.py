import re
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_uninfo import Uninfo
from nonebot.plugin import PluginMetadata

# 显式导入需要的数据库函数，避免*导入带来的命名冲突
from mengluo_vrc_bot.services.db import execute, fetchone

from .data_source import get_user_name

__plugin_meta__ = PluginMetadata(
    name="用户绑定",
    description="绑定VRC用户ID",
    usage="""
    绑定用户：绑定VRC用户ID，格式为usr_前缀+UUID
    我的绑定：查看当前绑定的VRC用户ID
    解绑用户：解绑当前绑定的VRC用户ID
    """,
)

# 提取正则表达式为常量，提高可读性
VRC_ID_PATTERN = r'^usr_[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'

bind_user = on_alconna(Alconna("绑定用户", Args["vrc_id", str]))
check_user = on_alconna(Alconna("我的绑定"))
unbind_user = on_alconna(Alconna("解绑用户"))

@bind_user.handle()
async def _(session: Uninfo, vrc_id: str):
    # 验证用户ID格式（使用常量提高可读性）
    if not re.match(VRC_ID_PATTERN, vrc_id):
        await bind_user.finish("错误：VRC用户ID格式不正确，需符合usr_前缀+UUID格式")
    user_name = await get_user_name(vrc_id)  # 使用从data_source.py导入的函数获取用户名称
    if not user_name:  # 检查用户是否存在
        await bind_user.finish(f"错误：未找到VRC用户：{vrc_id}")  # 明确提示用户不存在，而不是返回Non
    user_id = session.user.id
        # 明确提示绑定的VRC ID
    if await fetchone("SELECT vrc_id FROM user_info WHERE user_id =?", user_id):
        await bind_user.finish(f"您已绑定过VRC用户：{user_name}，如需更换请先解绑！")
    elif await fetchone("SELECT vrc_id FROM user_info WHERE vrc_id =?", vrc_id):
        await bind_user.finish(f"该VRC用户：{user_name}已被其他用户绑定！")
    else:
        await execute("INSERT INTO user_info (user_id, vrc_id) VALUES (?, ?)", user_id, vrc_id)
        await bind_user.finish(f"绑定成功！您已绑定VRC用户：{user_name}")

@check_user.handle()
async def _(session: Uninfo):
    user_id = session.user.id
    result = await fetchone("SELECT vrc_id FROM user_info WHERE user_id = ?", user_id)
    if result:
        # 明确解包元组提高可读性
        vrc_id, = result
        user_name = await get_user_name(vrc_id)
        await check_user.finish(f"您当前绑定的VRC用户：{user_name}")
    else:
        await check_user.finish("您还没有绑定任何VRC用户！")

@unbind_user.handle()
async def _(session: Uninfo):
    user_id = session.user.id
    result = await fetchone("SELECT vrc_id FROM user_info WHERE user_id =?", user_id)
    if result:
        # 明确解包元组提高可读性
        vrc_id, = result
        user_name = await get_user_name(vrc_id)
        await execute("DELETE FROM user_info WHERE user_id =?", user_id)
        await unbind_user.finish(f"解绑成功！您已解绑VRC用户：{user_name}")
    else:
        await unbind_user.finish("您还没有绑定任何VRC用户！")