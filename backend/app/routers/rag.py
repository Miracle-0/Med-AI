from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models.chapter import Chapter
from app.services.rag_service import rag_service

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    citations: List[dict]
    source_chunks: List[str]

@router.post("/index")
async def build_index(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """建立向量索引"""
    result = await db.execute(select(Chapter).where(Chapter.textbook_id == textbook_id))
    chapters = result.scalars().all()

    if not chapters:
        raise HTTPException(status_code=404, detail="未找到教材章节")

    chunks_count = await rag_service.build_index(chapters, textbook_id)

    return {
        "textbook_id": textbook_id,
        "chunks_count": chunks_count,
        "status": "indexed"
    }

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    """RAG问答"""
    answer, chunks = await rag_service.query(request.query)

    citations = []
    source_chunks = []

    for chunk in chunks:
        citations.append({
            "textbook": chunk["textbook_id"],
            "chapter": chunk["chapter_id"],
            "page": chunk["page"],
            "relevance_score": chunk["relevance_score"]
        })
        source_chunks.append(chunk["content"])

    return QueryResponse(
        answer=answer,
        citations=citations,
        source_chunks=source_chunks
    )

@router.get("/status")
async def get_status():
    """获取索引状态"""
    return rag_service.get_status()
