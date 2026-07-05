"""天气数据访问 — 和风天气 API + 30min 内存缓存

无 API Key 或 API 调用失败时，不返回虚拟天气数据，
相关字段一律返回 N/A，前端据此显示"天气暂不可用"。
"""
import httpx
from repository.cache_repo import cache_repo
from config import settings

# 和风天气图标代码 → 简化天气描述映射
WEATHER_ICON_MAP = {
    "100": "晴", "101": "多云", "102": "少云", "103": "晴间多云",
    "104": "阴", "300": "阵雨", "301": "强阵雨", "302": "雷阵雨",
    "303": "强雷阵雨", "304": "雷阵雨伴有冰雹", "305": "小雨", "306": "中雨",
    "307": "大雨", "308": "极端降雨", "309": "毛毛雨", "310": "暴雨",
    "311": "大暴雨", "312": "特大暴雨", "313": "冻雨", "400": "小雪",
    "401": "中雪", "402": "大雪", "403": "暴雪", "404": "雨夹雪",
    "500": "薄雾", "501": "雾", "502": "霾", "503": "扬沙", "504": "浮尘",
}

# 城市名 → 和风 LocationID 的简化映射（实际应通过 /geo/v2/city/lookup 查询）
CITY_LOCATION_MAP = {
    "北京": "101010100", "上海": "101020100", "广州": "101280101",
    "深圳": "101280601", "成都": "101270101", "杭州": "101210101",
    "西安": "101110101", "重庆": "101040100",
}

NA = "N/A"

# In-memory cache for dynamic city lookups
_location_cache: dict[str, str] = {}


async def _resolve_location(city: str) -> str | None:
    """Resolve city name to QWeather Location ID via geo API."""
    # Check hardcoded map first
    if city in CITY_LOCATION_MAP:
        return CITY_LOCATION_MAP[city]
    # Check runtime cache
    if city in _location_cache:
        return _location_cache[city]
    # Look up via API
    if not settings.QWEATHER_API_KEY:
        return None
    try:
        async with httpx.AsyncClient(timeout=5, proxy=None, trust_env=False) as client:
            resp = await client.get(
                f"{settings.QWEATHER_BASE}/v2/city/lookup",
                params={"location": city, "key": settings.QWEATHER_API_KEY},
            )
            resp.raise_for_status()
            data = resp.json()
            if data.get("code") == "200" and data.get("location"):
                loc_id = data["location"][0]["id"]
                _location_cache[city] = loc_id
                return loc_id
    except Exception:
        pass
    return None


def _na_weather(city: str, reason: str = "") -> dict:
    """无真实数据时的 N/A 占位（非虚拟数据）"""
    return {
        "city": city,
        "temp": NA,
        "feels_like": NA,
        "weather": NA,
        "icon": NA,
        "humidity": NA,
        "wind": NA,
        "update_time": "",
        "na_reason": reason or "天气服务未配置",
    }


class WeatherRepository:
    async def get_current(self, city: str) -> dict:
        """获取实时天气：内存缓存 30min → 和风 API → N/A 兜底"""
        cache_key = f"weather:{city}"
        cached = await cache_repo.get(cache_key)
        if cached:
            cached["from_cache"] = True
            return cached

        weather = await self._fetch_from_api(city)
        if weather is None:
            # 无 API Key 或调用失败，返回 N/A（不缓存 N/A，避免持续返回不可用）
            na = _na_weather(city, "和风天气 API 未配置或调用失败" if not settings.QWEATHER_API_KEY else "和风天气 API 调用失败")
            na["from_cache"] = False
            return na

        await cache_repo.set(cache_key, weather, ttl=1800)
        weather["from_cache"] = False
        return weather

    async def _fetch_from_api(self, city: str) -> dict | None:
        if not settings.QWEATHER_API_KEY:
            return None
        location = await _resolve_location(city)
        if not location:
            return None
        try:
            async with httpx.AsyncClient(timeout=5, proxy=None, trust_env=False) as client:
                resp = await client.get(
                    f"{settings.QWEATHER_BASE}/v7/weather/now",
                    params={"location": location, "key": settings.QWEATHER_API_KEY},
                )
                resp.raise_for_status()
                data = resp.json().get("now", {})
                return {
                    "city": city,
                    "temp": int(data.get("temp", 20)),
                    "feels_like": int(data.get("feelsLike", 20)),
                    "weather": WEATHER_ICON_MAP.get(data.get("icon", ""), data.get("text", "晴")),
                    "icon": data.get("icon", "100"),
                    "humidity": int(data.get("humidity", 50)),
                    "wind": f"{data.get('windDir', '微风')} {data.get('windScale', '1')}级",
                    "update_time": data.get("obsTime", ""),
                }
        except Exception:
            return None


weather_repo = WeatherRepository()
