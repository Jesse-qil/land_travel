"""城市/路书路由"""
from fastapi import APIRouter, Query
from schemas.common import ok, fail, ErrorCodes
from service.city_service import city_service

router = APIRouter()


@router.get("/cities")
async def list_cities(
    tag: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(60, ge=1, le=500),
):
    data = await city_service.list_cities(tag, search, page, size)
    return ok(data)


@router.get("/plans/{city}")
async def get_plan(city: str):
    plan = await city_service.get_plan(city)
    if not plan:
        return fail(ErrorCodes.NOT_FOUND, f"未找到 {city} 的路书")
    return ok(plan)
