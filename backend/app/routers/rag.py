from fastapi import APIRouter

router = APIRouter()

@router.post("/query")
async def rag_query():
    """RAG问答"""
    return {"message": "TODO: 实现RAG问答"}
