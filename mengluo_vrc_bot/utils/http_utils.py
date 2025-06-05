from typing import Any

import httpx
from httpx import Response
from retrying import retry


USER_AGENT = {"User-Agent": "mengluo_vrc_bot/1.0"}

class AsyncHttpx:

    @classmethod
    @retry(stop_max_attempt_number=3)
    async def get(
        cls,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        timeout: int = 30,  # noqa: ASYNC109
        **kwargs,
    ) -> Response:
        """Get

        参数:
            url: url
            params: params
            headers: 请求头
            cookies: cookies
            verify: verify
            timeout: 超时时间
        """
        if not headers:
            headers = USER_AGENT
        async with httpx.AsyncClient(verify=verify) as client:  # type: ignore
            return await client.get(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )

    @classmethod
    async def head(
        cls,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        verify: bool = True,
        timeout: int = 30,  # noqa: ASYNC109
        **kwargs,
    ) -> Response:
        """Head

        参数:
            url: url
            params: params
            headers: 请求头
            cookies: cookies
            verify: verify
            timeout: 超时时间
        """
        if not headers:
            headers = USER_AGENT
        async with httpx.AsyncClient(verify=verify) as client:  # type: ignore
            return await client.head(
                url,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )

    @classmethod
    async def post(
        cls,
        url: str,
        *,
        data: dict[str, Any] | None = None,
        content: Any = None,
        files: Any = None,
        verify: bool = True,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
        timeout: int = 30,  # noqa: ASYNC109
        **kwargs,
    ) -> Response:
        """
        说明:
            Post
        参数:
            url: url
            data: data
            content: content
            files: files
            json: json
            params: params
            headers: 请求头
            cookies: cookies
            timeout: 超时时间
        """
        if not headers:
            headers = USER_AGENT
        async with httpx.AsyncClient(verify=verify) as client:  # type: ignore
            return await client.post(
                url,
                content=content,
                data=data,
                files=files,
                json=json,
                params=params,
                headers=headers,
                cookies=cookies,
                timeout=timeout,
                **kwargs,
            )