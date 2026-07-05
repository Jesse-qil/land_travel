"""城市/路书业务层"""
from repository.city_repo import city_repo


class CityService:
    async def list_cities(
        self, tag: str | None = None, search: str | None = None,
        page: int = 1, size: int = 20,
    ) -> dict:
        items, total = await city_repo.list_cities(tag, search, page, size)
        return {"items": items, "total": total, "page": page, "size": size}

    async def get_plan(self, city: str) -> dict | None:
        return await city_repo.get_plan(city)

    async def get_city(self, city: str) -> dict | None:
        return await city_repo.get_city(city)


city_service = CityService()
