"""天气路由"""
from fastapi import APIRouter
from schemas.common import ok, fail, ErrorCodes
from service.weather_service import weather_service

router = APIRouter()


@router.get("/weather/{city}")
async def get_weather(city: str):
    data = await weather_service.get_current(city)
    if not data:
        return fail(ErrorCodes.NOT_FOUND, f"未找到 {city} 的天气数据")
    return ok(data)
