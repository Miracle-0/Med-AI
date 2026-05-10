from fastapi import APIRouter

router = APIRouter()

@router.post("/send")
async def send_message():
    """发送对话消息"""
    return {"message": "TODO: 实现对话功能"}
