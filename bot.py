import nonebot
from nonebot.adapters.onebot.v11 import Adapter
from mengluo_vrc_bot.services.db import init_db

# 初始化 NoneBot
nonebot.init()

# 注册适配器
driver = nonebot.get_driver()
driver.register_adapter(Adapter)

# 在这里加载插件
nonebot.load_plugins("mengluo_vrc_bot/plugins")  # 本地插件

if __name__ == "__main__":
    init_db()
    nonebot.run()