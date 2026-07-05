"""天气业务层 — 代理 + 缓存"""
from repository.weather_repo import weather_repo


class WeatherService:
    async def get_current(self, city: str) -> dict | None:
        try:
            return await weather_repo.get_current(city)
        except Exception:
            return None


weather_service = WeatherService()
