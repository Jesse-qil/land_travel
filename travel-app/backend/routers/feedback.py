"""反馈路由：路书点赞/点踩"""
from fastapi import APIRouter
from schemas.common import ok

router = APIRouter()


@router.post("/feedback")
async def feedback(body: dict):
    # TODO: 入库记录 like/dislike
    return ok(message="感谢反馈")
