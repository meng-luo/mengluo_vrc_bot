## 梦落_VRC BOT

> 请注意：本项目仍在开发过程中，可能存在一些问题，欢迎提 issue 和 pr。

本项目符合 [OneBot](https://github.com/howmanybots/onebot) 标准，可基于以下项目与机器人框架/平台进行交互

|                           项目地址                            | 平台 |         核心作者         | 备注 |
| :-----------------------------------------------------------: | :--: | :----------------------: | :--: |
|       [LLOneBot](https://github.com/LLOneBot/LLOneBot)        | NTQQ |        linyuchen         | 可用 |
|         [Napcat](https://github.com/NapNeko/NapCatQQ)         | NTQQ |         NapNeko          | 可用 |
| [Lagrange.Core](https://github.com/LagrangeDev/Lagrange.Core) | NTQQ | LagrangeDev/Linwenxuan04 | 可用 |

## 📋 功能列表

- [x] vrchat 链接解析
- [x] vrchat 用户、地图、群组、世界查询
- [x] QQ账号绑定
- [x] B站解析
- [x] 群友查询
- [-] 好友查询

## 🔧 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置机器人

```bash
cp .env.example .env.dev
```

修改 `.env.dev` 文件，填写机器人的相关配置，如机器人超级用户、 VRChat账号信息

### 3. 启动机器人

```bash
python bot.py
```

## 🙏 感谢

[botuniverse / onebot](https://github.com/botuniverse/onebot) ：超棒的机器人协议  
[nonebot / nonebot2](https://github.com/nonebot/nonebot2) ：跨平台 Python 异步机器人框架  
[zhenxun-org / zhenxun_bot](https://github.com/zhenxun-org/zhenxun_bot) ：基于 nonebot2 的绪山真寻 Bot
[vrcx-team / VRCX](https://github.com/vrcx-team/VRCX) ：一款用于 VRChat 的外部辅助小工具