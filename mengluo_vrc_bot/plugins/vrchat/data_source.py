import requests

from mengluo_vrc_bot.services.account_refresh import get_cookie, update_cookie
from mengluo_vrc_bot.services.log import logger


BASE_API_URL = "https://api.vrchat.cloud/api/1/"  # 提取基础API URL常量
USER_AGENT = "mengluo_vrc_bot/1.0"


async def request(url, method="GET", **kwargs) -> dict | None:
    headers = {
        "Cookie": await get_cookie(),  # 使用从文件中读取的Cookie
        "User-Agent": USER_AGENT  # 使用自定义User-Agent
    }
    try:
        response = requests.request(method, url, **kwargs, headers=headers)
        if response.status_code == 401:  # 检查是否需要更新Cookie
            cookie = "auth=" + await update_cookie()  # 更新Cookie
            headers["Cookie"] = cookie  # 更新请求头中的Cookie
            response = requests.request(method, url, **kwargs, headers=headers)  # 重新发送请求        response.raise_for_status()
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"请求失败: {e}")
        return None


async def get_avatar(id):
    url = f"{BASE_API_URL}avatars/{id}"
    return await request(url)


async def get_user(id):
    url = f"{BASE_API_URL}users/{id}"
    return await request(url)


async def get_group(id):
    url = f"{BASE_API_URL}groups/{id}"
    return await request(url)


async def get_world(id):
    url = f"{BASE_API_URL}worlds/{id}"
    return await request(url)


async def get_user_groups(id):
    url = f"{BASE_API_URL}users/{id}/groups"
    return await request(url)


async def get_user_current_group(id):
    url = f"{BASE_API_URL}users/{id}/groups/represented"
    return await request(url)


async def get_file_info(id):
    url = f"{BASE_API_URL}file/{id}"
    return await request(url)
