import nonebot
import os

nonebot.require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import text_to_pic

async def render_help():
    """
    生成帮助图片
    """
    plugin_text = ""
    for dir in os.listdir("mengluo_vrc_bot/plugins"):
        plugin: Plugin | None = nonebot.get_plugin(dir)
        if not plugin.metadata:
            plugin_text = plugin_text + f"插件名称：{dir}\n插件描述：无\n插件用法：无\n\n"
            continue
        else:
            plugin_name = plugin.metadata.name
            plugin_description = plugin.metadata.description
            plugin_usage = plugin.metadata.usage
            plugin_text = plugin_text + f"插件名称：{plugin_name}\n插件描述：{plugin_description}\n插件用法：{plugin_usage}\n\n"
    return await text_to_pic(plugin_text)