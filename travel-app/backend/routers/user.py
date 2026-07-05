"""用户/UGC 路由：评论/收藏/自定义行程"""
from fastapi import APIRouter, Request
from schemas.common import ok, fail, ErrorCodes

router = APIRouter()


def _require_login(request: Request):
    if not request.state.user_id:
        return fail(ErrorCodes.UNAUTHORIZED, "请先登录")
    return None


@router.get("/comments")
async def list_comments(city_id: str, page: int = 1, size: int = 20):
    # TODO: 接入 user_service.list_comments
    return ok({"items": [], "total": 0})


@router.post("/comments")
async def create_comment(request: Request, body: dict):
    if err := _require_login(request):
        return err
    # TODO: 敏感词过滤 + 入库
    return ok(message="评论成功")


@router.delete("/comments/{comment_id}")
async def delete_comment(request: Request, comment_id: str):
    if err := _require_login(request):
        return err
    return ok(message="已删除")


@router.get("/favorites")
async def list_favorites(request: Request):
    if err := _require_login(request):
        return err
    return ok({"items": []})


@router.post("/favorites")
async def add_favorite(request: Request, body: dict):
    if err := _require_login(request):
        return err
    return ok(message="已收藏")


@router.delete("/favorites/{city_id}")
async def remove_favorite(request: Request, city_id: str):
    if err := _require_login(request):
        return err
    return ok(message="已取消收藏")


@router.get("/user/plan")
async def get_user_plan(request: Request, city_id: str):
    if err := _require_login(request):
        return err
    return ok({"city_id": city_id, "plan_data": None, "version": 0})


@router.post("/user/plan")
async def save_user_plan(request: Request, body: dict):
    if err := _require_login(request):
        return err
    # TODO: 版本冲突检测
    return ok({"version": 1})
