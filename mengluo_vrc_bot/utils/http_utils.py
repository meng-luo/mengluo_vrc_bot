from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from httpx import AsyncHTTPTransport, HTTPStatusError, Response

from mengluo_vrc_bot.services.log import logger

CLIENT_KEY = ["use_proxy", "proxy", "verify", "headers"]
USER_AGENT = {"User-Agent": "mengluo_vrc_bot/1.0"}

def get_async_client(verify: bool = False, **kwargs) -> httpx.AsyncClient:
    """创建 httpx.AsyncClient 实例。
    
    参数:
        verify: 是否验证 SSL 证书。
        **kwargs: 其他传递给 httpx.AsyncClient 的参数。
        
    返回:
        httpx.AsyncClient: 配置好的客户端实例。
    """
    transport = kwargs.pop("transport", None) or AsyncHTTPTransport(verify=verify)
    return httpx.AsyncClient(transport=transport, **kwargs)


class AsyncHttpx:
    """异步 HTTP 客户端工具类。"""

    @classmethod
    @asynccontextmanager
    async def _create_client(
        cls,
        *,
        headers: dict[str, str] | None = None,
        verify: bool = False,
        **kwargs,
    ) -> AsyncGenerator[httpx.AsyncClient, None]:
        """创建一个私有的、配置好的 httpx.AsyncClient 上下文管理器。

        参数:
            headers: 需要合并到客户端的自定义请求头。
            verify: 是否验证 SSL 证书。
            **kwargs: 其他所有传递给 httpx.AsyncClient 的参数。

        返回:
            AsyncGenerator[httpx.AsyncClient, None]: 客户端生成器。
        """
        final_headers = USER_AGENT
        if headers:
            final_headers.update(headers)

        async with get_async_client(
            verify=verify, headers=final_headers, **kwargs
        ) as client:
            yield client

    @classmethod
    async def get(
        cls,
        url: str,
        *,
        check_status_code: int | None = None,
        **kwargs,
    ) -> Response:
        """发送 GET 请求。

        说明:
            本方法是 httpx.get 的高级包装，提供了统一的客户端管理。

        参数:
            url: 请求的 URL。
            check_status_code: (可选) 若提供，将检查响应状态码是否匹配，否则抛出异常。
            **kwargs: 其他所有传递给 httpx.get 的参数
                    (如 `params`, `headers`, `timeout`等)。

        返回:
            Response: HTTP 响应对象。
            
        异常:
            HTTPStatusError: 当响应状态码与期望不匹配时。
        """
        logger.info(f"开始获取 {url}..")
        client_kwargs = {k: v for k, v in kwargs.items() if k in CLIENT_KEY}
        for key in CLIENT_KEY:
            kwargs.pop(key, None)
        async with cls._create_client(**client_kwargs) as client:
            response = await client.get(url, **kwargs)

        if check_status_code and response.status_code != check_status_code:
            raise HTTPStatusError(
                f"状态码错误: {response.status_code}!={check_status_code}",
                request=response.request,
                response=response,
            )
        return response

    @classmethod
    async def head(cls, url: str, **kwargs) -> Response:
        """发送 HEAD 请求。

        说明:
            本方法是对 httpx.head 的封装，通常用于检查资源的元信息（如大小、类型）。

        参数:
            url: 请求的 URL。
            **kwargs: 其他所有传递给 httpx.head 的参数
                        (如 `headers`, `timeout`, `allow_redirects`)。

        返回:
            Response: HTTP 响应对象。
        """
        client_kwargs = {k: v for k, v in kwargs.items() if k in CLIENT_KEY}
        for key in CLIENT_KEY:
            kwargs.pop(key, None)
        async with cls._create_client(**client_kwargs) as client:
            return await client.head(url, **kwargs)

    @classmethod
    async def post(cls, url: str, **kwargs) -> Response:
        """发送 POST 请求。

        说明:
            本方法是对 httpx.post 的封装，提供了统一的客户端管理。

        参数:
            url: 请求的 URL。
            **kwargs: 其他所有传递给 httpx.post 的参数
                        (如 `data`, `json`, `content` 等)。

        返回:
            Response: HTTP 响应对象。
        """
        client_kwargs = {k: v for k, v in kwargs.items() if k in CLIENT_KEY}
        for key in CLIENT_KEY:
            kwargs.pop(key, None)
        async with cls._create_client(**client_kwargs) as client:
            return await client.post(url, **kwargs)