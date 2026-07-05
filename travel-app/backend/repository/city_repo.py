"""城市/路书数据访问 — DB优先 → LRU → JSON 三级兜底"""
import json
from pathlib import Path
from typing import Any

from repository.cache_repo import cache_repo
from config import settings

DATA_DIR = settings.DATA_DIR
_CITIES_CACHE: dict | None = None
_PLANS_CACHE: dict | None = None


def _load_cities_json() -> dict:
    global _CITIES_CACHE
    if _CITIES_CACHE is None:
        path = DATA_DIR / "cities_backup.json"
        if path.exists():
            _CITIES_CACHE = json.loads(path.read_text(encoding="utf-8"))
        else:
            _CITIES_CACHE = {"cities": []}
    return _CITIES_CACHE


def _load_plans_json() -> dict:
    global _PLANS_CACHE
    if _PLANS_CACHE is None:
        path = DATA_DIR / "plans_backup.json"
        if path.exists():
            _PLANS_CACHE = json.loads(path.read_text(encoding="utf-8"))
        else:
            _PLANS_CACHE = {"plans": {}}
    return _PLANS_CACHE


def _resolve_city_id(city: str) -> str | None:
    """城市名/拼音 → city_id"""
    data = _load_cities_json()
    for c in data["cities"]:
        if city in (c["name"], c["pinyin"], c["id"]):
            return c["id"]
    return None


class CityRepository:
    async def list_cities(
        self,
        tag: str | None = None,
        search: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> tuple[list[dict], int]:
        # TODO: Supabase 接入后优先查 DB，失败降级 JSON
        data = _load_cities_json()
        items = data["cities"]

        if tag:
            items = [c for c in items if tag in c.get("tags", [])]
        if search:
            kw = search.lower()
            items = [
                c for c in items
                if kw in c["name"].lower() or kw in c["pinyin"].lower()
            ]

        items = sorted(items, key=lambda x: x.get("sort_weight", 0), reverse=True)
        total = len(items)
        start = (page - 1) * size
        return items[start : start + size], total

    async def get_city(self, city: str) -> dict | None:
        city_id = _resolve_city_id(city)
        if not city_id:
            return None
        data = _load_cities_json()
        for c in data["cities"]:
            if c["id"] == city_id:
                return c
        return None

    async def get_plan(self, city: str) -> dict | None:
        # 先查 LRU 缓存
        city_id = _resolve_city_id(city)
        if not city_id:
            return None

        cache_key = f"plan:{city_id}"
        cached = await cache_repo.get(cache_key)
        if cached:
            return cached

        # TODO: Supabase 接入后查 city_plans 表
        data = _load_plans_json()
        plan = data["plans"].get(city_id)
        if plan:
            await cache_repo.set(cache_key, plan, ttl=3600)
        return plan


city_repo = CityRepository()
