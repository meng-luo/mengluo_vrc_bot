import re
from nonebot_plugin_alconna import Alconna, Args, on_alconna
from nonebot_plugin_uninfo import Uninfo

# 显式导入需要的数据库函数，避免*导入带来的命名冲突
from ...services.db import execute, fetchone

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
    user_id = session.user.id
        # 明确提示绑定的VRC ID
    if await fetchone("SELECT vrc_id FROM user_info WHERE user_id =?", user_id):
        await bind_user.finish(f"您已绑定过VRC用户：{vrc_id}，如需更换请先解绑！")
    elif await fetchone("SELECT vrc_id FROM user_info WHERE vrc_id =?", vrc_id):
        await bind_user.finish(f"该VRC用户：{vrc_id}已被其他用户绑定！")
    else:
        await execute("INSERT INTO user_info (user_id, vrc_id) VALUES (?, ?)", user_id, vrc_id)
        await bind_user.finish(f"绑定成功！您已绑定VRC用户：{vrc_id}")

@check_user.handle()
async def _(session: Uninfo):
    user_id = session.user.id
    result = await fetchone("SELECT vrc_id FROM user_info WHERE user_id = ?", user_id)
    if result:
        # 明确解包元组提高可读性
        vrc_id, = result
        await check_user.finish(f"您当前绑定的VRC用户：{vrc_id}")
    else:
        await check_user.finish("您还没有绑定任何VRC用户！")

@unbind_user.handle()
async def _(session: Uninfo):
    user_id = session.user.id
    result = await fetchone("SELECT vrc_id FROM user_info WHERE user_id =?", user_id)
    if result:
        # 明确解包元组提高可读性
        vrc_id, = result
        await execute("DELETE FROM user_info WHERE user_id =?", user_id)
        await unbind_user.finish(f"解绑成功！您已解绑VRC用户：{vrc_id}")
    else:
        await unbind_user.finish("您还没有绑定任何VRC用户！")