"""后端代理 — Agent 通过此层反查主项目数据，不直连任何数据源"""
import httpx
from config import settings


class BackendProxy:
    """Agent 不直连数据库/第三方 API，统一通过主项目 API 获取数据"""

    def __init__(self, base_url: str | None = None, service_token: str | None = None):
        self.base_url = base_url or settings.BACKEND_BASE_URL
        self.service_token = service_token or settings.BACKEND_SERVICE_TOKEN

    async def _get(self, path: str) -> dict:
        headers = {"X-Service-Token": self.service_token}
        async with httpx.AsyncClient(timeout=10, proxy=None, trust_env=False) as client:
            resp = await client.get(f"{self.base_url}{path}", headers=headers)
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {})
            return {}

    async def get_weather(self, city: str) -> dict:
        return await self._get(f"/api/weather/{city}")

    async def get_plan(self, city: str) -> dict:
        return await self._get(f"/api/plans/{city}")


backend_proxy = BackendProxy()
