from nonebot_plugin_alconna import Alconna, on_alconna, UniMessage
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata

from .data_source import render_help


help = on_alconna(Alconna("帮助"), aliases={"help", "功能", "菜单"}, rule=to_me(), priority=5, block=True)

__plugin_meta__ = PluginMetadata(
    name="帮助",
    description="查看帮助",
    usage="""
    帮助：查看帮助
    """,
)

@help.handle()
async def _():
    img = await render_help()
    await UniMessage.image(raw=img).send()
    # await help.finish(img)