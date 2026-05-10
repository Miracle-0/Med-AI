from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import llm_service

router = APIRouter()

chat_histories: Dict[str, List[Dict]] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    """发送对话消息"""
    session_id = request.session_id

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    chat_histories[session_id].append({
        "role": "user",
        "content": request.message
    })

    system_prompt = """你是一个学科知识整合助手，可以帮助教师理解和优化教材整合方案。

你可以：
1. 解释整合决策的理由
2. 根据教师反馈调整整合方案
3. 回答关于知识点关系的问题

请用专业、友好的语气回答。"""

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_histories[session_id][-10:])

    response = await llm_service.generate(
        request.message,
        system_prompt
    )

    chat_histories[session_id].append({
        "role": "assistant",
        "content": response
    })

    return ChatResponse(
        response=response,
        session_id=session_id
    )

@router.get("/history")
async def get_chat_history(session_id: str = "default"):
    """获取对话历史"""
    return chat_histories.get(session_id, [])
