import json
from typing import Dict, Optional

import aiohttp
import nonebot
from mengluo_vrc_bot.services.log import logger
from mengluo_vrc_bot.config.path import DATA_PATH

config = nonebot.get_driver().config
account_info = config.vrc_account

# 常量定义
VRC_API_BASE = "https://api.vrchat.cloud/api/1"
USER_AGENT = "mengluo_vrc_bot/1.0"
COOKIE_FILE = DATA_PATH / "cookie.json"


class VRCAuthError(Exception):
    """VRChat认证相关异常"""
    pass


async def _make_request(
    method: str, 
    url: str, 
    headers: Dict[str, str], 
    json_data: Optional[Dict] = None
) -> Optional[aiohttp.ClientResponse]:
    """统一的HTTP请求方法"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                return response
    except aiohttp.ClientError as e:
        logger.error(f"请求失败: {e}")
        return None


def _parse_cookies(set_cookie_header: str) -> Dict[str, str]:
    """解析Set-Cookie头部"""
    cookies_dict = {}
    if not set_cookie_header:
        return cookies_dict
    
    # 处理多个cookie的情况
    cookie_parts = set_cookie_header.split(',')
    for part in cookie_parts:
        cookie_item = part.split(';')[0].strip()
        if '=' in cookie_item:
            key, value = cookie_item.split('=', 1)
            cookies_dict[key.strip()] = value.strip()
    
    return cookies_dict


async def refresh_token() -> Optional[Dict[str, str]]:
    """刷新令牌获取新的cookies"""
    url = f"{VRC_API_BASE}/auth/user"
    headers = {
        "Authorization": f"Basic {account_info}",
        "User-Agent": USER_AGENT
    }
    
    response = await _make_request("GET", url, headers)
    if not response:
        return None
    
    try:
        set_cookie_header = response.headers.get('Set-Cookie')
        if not set_cookie_header:
            logger.error("响应中未找到Set-Cookie头部")
            return None
        
        cookies_dict = _parse_cookies(set_cookie_header)
        if not cookies_dict.get('auth'):
            logger.error("未找到auth cookie")
            return None
        
        # 验证cookie是否有效
        if await test_cookie(f"auth={cookies_dict['auth']}"):
            return cookies_dict
        else:
            logger.error("获取的cookie无效")
            return None
            
    except Exception as e:
        logger.error(f"处理响应时出错: {e}")
        return None


async def update_cookie() -> str:
    """更新并保存cookie"""
    cookies_dict = await refresh_token()
    if not cookies_dict:
        raise VRCAuthError("无法获取有效的Cookie")
    
    try:
        # 保存cookie到文件
        with open(COOKIE_FILE, "w", encoding='utf-8') as f:
            json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
        
        logger.info("Cookie已成功更新")
        return cookies_dict.get("auth", "")
        
    except IOError as e:
        logger.error(f"保存cookie文件失败: {e}")
        raise VRCAuthError(f"保存cookie文件失败: {e}")


async def get_cookie() -> str:
    """获取cookie，如果不存在则自动更新"""
    try:
        if not COOKIE_FILE.exists():
            logger.info("Cookie文件不存在，开始创建")
            await update_cookie()
        
        with open(COOKIE_FILE, "r", encoding='utf-8') as f:
            auth_data = json.load(f)
        
        if not isinstance(auth_data, dict) or 'auth' not in auth_data:
            logger.warning("Cookie文件格式错误，重新获取")
            await update_cookie()
            with open(COOKIE_FILE, "r", encoding='utf-8') as f:
                auth_data = json.load(f)
        
        return f"auth={auth_data['auth']}"
        
    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"读取cookie文件失败: {e}")
        # 文件损坏时重新获取
        await update_cookie()
        with open(COOKIE_FILE, "r", encoding='utf-8') as f:
            auth_data = json.load(f)
        return f"auth={auth_data['auth']}"


async def test_cookie(cookie: str) -> bool:
    """测试cookie是否有效"""
    url = f"{VRC_API_BASE}/auth/user"
    headers = {
        "Cookie": cookie,
        "User-Agent": USER_AGENT
    }
    
    response = await _make_request("GET", url, headers)
    if not response:
        return False
    
    try:
        if response.status == 401:
            logger.error("认证失败：账号或密码错误")
            return False
        
        response_data = await response.json()
        
        # 需要两步验证
        if response_data.get("requiresTwoFactorAuth"):
            return await handle_two_factor_auth(cookie)
        
        # 检查是否有有效的用户信息
        if response_data.get("id"):
            logger.info("Cookie验证成功")
            return True
        
        logger.warning("Cookie验证失败：响应数据异常")
        return False
        
    except Exception as e:
        logger.error(f"验证cookie时出错: {e}")
        return False


async def handle_two_factor_auth(cookie: str) -> bool:
    """处理两步验证"""
    url = f"{VRC_API_BASE}/auth/twofactorauth/totp/verify"
    headers = {
        "Cookie": cookie,
        "User-Agent": USER_AGENT
    }

    while True:
        try:
            # 注意：在生产环境中，应该通过更安全的方式获取验证码
            # 比如通过配置文件、环境变量或外部接口
            print(f"请输入两步验证码: ", end="")
            code = input().strip()
            
            if not code:
                logger.warning("验证码不能为空")
                continue
            
            data = {"code": code}
            response = await _make_request("POST", url, headers, data)
            
            if not response:
                logger.error("请求失败")
                continue
            
            if response.status == 200:
                logger.info("两步验证成功")
                return True
            elif response.status == 401:
                logger.error("验证码错误")
            else:
                logger.error(f"未知错误，状态码: {response.status}")
                
        except Exception as e:
            logger.error(f"两步验证时出错: {e}")

async def ensure_valid_cookie() -> str:
    """确保获取到有效的cookie"""
    try:
        cookie = await get_cookie()
        if await test_cookie(cookie):
            return cookie
        
        # 如果当前cookie无效，尝试刷新
        logger.info("当前cookie无效，尝试刷新")
        await update_cookie()
        return await get_cookie()
        
    except Exception as e:
        logger.error(f"获取有效cookie失败: {e}")
        raise VRCAuthError(f"获取有效cookie失败: {e}")
