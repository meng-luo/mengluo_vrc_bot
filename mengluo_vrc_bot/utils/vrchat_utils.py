from typing import Dict, Union
from .http_utils import AsyncHttpx
from mengluo_vrc_bot.services.account_refresh import get_cookie, update_cookie
from mengluo_vrc_bot.services.log import logger


class VRChatAPIError(Exception):
    """VRChat API相关异常"""
    pass


class VRChatAPI:
    """VRChat API工具类"""
    
    BASE_URL = "https://api.vrchat.cloud/api/1/"
    
    def __init__(self):
        self._cookie_updated = False  # 避免重复更新cookie
    
    async def _make_request(self, endpoint: str, **kwargs) -> Union[Dict, str]:
        """
        统一的API请求方法
        
        Args:
            endpoint: API端点路径
            **kwargs: 传递给HTTP请求的额外参数
            
        Returns:
            API响应数据或错误信息
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            # 第一次请求
            cookie = await get_cookie()
            response = await AsyncHttpx.get(url, cookies=cookie, **kwargs)
            
            # 处理认证失败
            if response.status_code == 401 and not self._cookie_updated:
                logger.info("检测到认证失败，正在更新Cookie...")
                self._cookie_updated = True
                cookie = await update_cookie()
                response = await AsyncHttpx.get(url, cookies=cookie, **kwargs)
            
            # 处理404错误
            if response.status_code == 404:
                error_msg = f"未找到资源: {endpoint}"
                logger.warning(error_msg)
                return error_msg
            
            # 检查其他HTTP错误
            response.raise_for_status()
            
            # 重置cookie更新标志
            self._cookie_updated = False
            
            return response.json()
            
        except Exception as e:
            error_msg = f"请求 {endpoint} 失败: {str(e)}"
            logger.error(error_msg)
            return f"错误：{error_msg}"
    async def get_avatar(self, avatar_id: str) -> Union[Dict, str]:
        """获取头像信息"""
        return await self._make_request(f"avatars/{avatar_id}")
    
    async def get_user(self, user_id: str) -> Union[Dict, str]:
        """获取用户信息"""
        return await self._make_request(f"users/{user_id}")
    
    async def get_group(self, group_id: str) -> Union[Dict, str]:
        """获取群组信息"""
        return await self._make_request(f"groups/{group_id}")
    
    async def get_world(self, world_id: str) -> Union[Dict, str]:
        """获取世界信息"""
        return await self._make_request(f"worlds/{world_id}")
    
    async def get_user_groups(self, user_id: str) -> Union[Dict, str]:
        """获取用户所属群组列表"""
        return await self._make_request(f"users/{user_id}/groups")
    
    async def get_user_current_group(self, user_id: str) -> Union[Dict, str]:
        """获取用户当前代表的群组"""
        return await self._make_request(f"users/{user_id}/groups/represented")
    
    async def get_file_info(self, file_id: str) -> Union[Dict, str]:
        """获取文件信息"""
        return await self._make_request(f"file/{file_id}")
    
    async def get_friends(self, friends_status: bool, number: int) -> Union[Dict, str]:
        """获取好友列表"""
        return await self._make_request(f"auth/user/friends?offset=0&n={number}&offline={friends_status}")