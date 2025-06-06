from nonebot_plugin_alconna import Alconna, Args, on_alconna

bilibili_parse = on_alconna(Alconna("解析", Args["url", str]), priority=5, block=True)

@bilibili_parse.handle()
async def _(url: str):
    if "bilibili.com" not in url or "BV" not in url:
        await bilibili_parse.finish("错误：请输入正确的Bilibili视频URL")
    else:
        await bilibili_parse.finish("https://vrchat.mengluo.work/"+ url)