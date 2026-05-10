from typing import List, Dict
from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm_service import llm_service

router = APIRouter()

chat_histories: Dict[str, List[Dict]] = {}

SYSTEM_PROMPT = """你是一个学科知识整合助手，可以帮助教师理解和优化教材整合方案。

你可以：
1. 解释整合决策的理由
2. 根据教师反馈调整整合方案
3. 回答关于知识点关系的问题
4. 基于教材内容进行知识问答

请用专业、友好的语气回答。回答时请基于已有的教材内容，如果不确定请如实说明。"""


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    session_id: str


@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest) -> ChatResponse:
    """发送对话消息（支持多轮上下文）"""
    session_id = request.session_id

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    # 添加用户消息到历史
    chat_histories[session_id].append({
        "role": "user",
        "content": request.message,
    })

    # 构建完整消息列表：system + 最近 10 轮对话
    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(chat_histories[session_id][-20:])  # 最近 20 条（10 轮）

    response = await llm_service.generate_with_messages(messages)

    # 添加助手回复到历史
    chat_histories[session_id].append({
        "role": "assistant",
        "content": response,
    })

    return ChatResponse(response=response, session_id=session_id)


@router.get("/history")
async def get_chat_history(session_id: str = "default") -> List[Dict]:
    """获取对话历史"""
    return chat_histories.get(session_id, [])
