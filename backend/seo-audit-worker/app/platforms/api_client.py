from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


@dataclass(slots=True)
class ApiResponse:
    status_code: int
    text: str
    json_data: Optional[Dict[str, Any]]
    url: str


class ApiClientHelper:
    def __init__(self, timeout: float = 20.0, follow_redirects: bool = True):
        self.timeout = timeout
        self.follow_redirects = follow_redirects

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Any = None,
        json: Any = None,
    ) -> ApiResponse:
        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=self.follow_redirects,
        ) as client:
            response = await client.request(
                method,
                url,
                headers=headers,
                params=params,
                data=data,
                json=json,
            )

        try:
            json_data = response.json()
        except Exception:
            json_data = None

        return ApiResponse(
            status_code=response.status_code,
            text=response.text,
            json_data=json_data,
            url=str(response.url),
        )

    async def get(self, url: str, **kwargs) -> ApiResponse:
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> ApiResponse:
        return await self.request("POST", url, **kwargs)
