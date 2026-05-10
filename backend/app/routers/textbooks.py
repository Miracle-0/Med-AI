from fastapi import APIRouter

router = APIRouter()

@router.get("/list")
async def list_textbooks():
    """获取教材列表"""
    return {"textbooks": []}

@router.post("/upload")
async def upload_textbook():
    """上传教材"""
    return {"message": "TODO: 实现教材上传"}
