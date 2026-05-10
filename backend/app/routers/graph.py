import asyncio
import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.knowledge import KnowledgeNode, KnowledgeEdge, MergeDecision
from app.models.chapter import Chapter
from app.services.extractor import extractor
from app.services.merger import merger

router = APIRouter()

# 全局进度存储
_extraction_progress: dict = {}


@router.post("/extract/{textbook_id}")
async def extract_knowledge(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """提取教材知识点"""
    result = await db.execute(select(Chapter).where(Chapter.textbook_id == textbook_id))
    chapters = result.scalars().all()

    if not chapters:
        raise HTTPException(status_code=404, detail="未找到教材章节")

    active_chapters = [ch for ch in chapters if ch.content and ch.content.strip()]
    total = len(active_chapters)
    _extraction_progress[textbook_id] = {
        "current": 0, "total": total, "phase": "extracting", "status": "running"
    }

    all_nodes = []
    all_edges = []

    try:
        for i, chapter in enumerate(active_chapters):
            _extraction_progress[textbook_id]["current"] = i + 1
            _extraction_progress[textbook_id]["chapter_name"] = chapter.title

            nodes = await extractor.extract_from_chapter(
                chapter.content, textbook_id, chapter.chapter_id, chapter.page_start
            )
            all_nodes.extend(nodes)

            edges = await extractor.identify_relations(nodes)
            all_edges.extend(edges)

        _extraction_progress[textbook_id]["phase"] = "saving"
        _extraction_progress[textbook_id]["status"] = "saving"

        for node in all_nodes:
            db.add(node)
        for edge in all_edges:
            db.add(edge)
        await db.commit()

        _extraction_progress[textbook_id]["status"] = "completed"
        _extraction_progress[textbook_id]["nodes_count"] = len(all_nodes)
        _extraction_progress[textbook_id]["edges_count"] = len(all_edges)

        return {
            "textbook_id": textbook_id,
            "nodes_count": len(all_nodes),
            "edges_count": len(all_edges)
        }
    except Exception as e:
        _extraction_progress[textbook_id]["status"] = "failed"
        _extraction_progress[textbook_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")


@router.get("/extract/{textbook_id}/progress")
async def get_extraction_progress(textbook_id: str):
    """获取提取进度 (SSE)"""
    async def event_generator():
        while True:
            progress = _extraction_progress.get(textbook_id, {"status": "idle"})
            yield f"data: {json.dumps(progress, ensure_ascii=False)}\n\n"
            if progress.get("status") in ("completed", "failed", "idle"):
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/nodes")
async def get_nodes(textbook_id: str = None, db: AsyncSession = Depends(get_db)):
    """获取知识点列表"""
    query = select(KnowledgeNode)
    if textbook_id:
        query = query.where(KnowledgeNode.textbook_id == textbook_id)
    result = await db.execute(query)
    nodes = result.scalars().all()
    return nodes


@router.get("/edges")
async def get_edges(textbook_id: str = None, db: AsyncSession = Depends(get_db)):
    """获取关系列表"""
    query = select(KnowledgeEdge)
    result = await db.execute(query)
    edges = result.scalars().all()
    return edges


@router.post("/merge")
async def merge_knowledge(db: AsyncSession = Depends(get_db)):
    """整合所有教材知识点"""
    result = await db.execute(select(KnowledgeNode))
    all_nodes = result.scalars().all()

    if len(all_nodes) < 2:
        return {"message": "知识点不足，无需整合"}

    duplicate_groups = await merger.find_duplicates(all_nodes)
    merged_nodes, decisions = await merger.execute_merge(all_nodes, duplicate_groups)

    for decision in decisions:
        db.add(decision)
    await db.commit()

    compression_ratio = merger.calculate_compression_ratio(all_nodes, merged_nodes)

    return {
        "original_count": len(all_nodes),
        "merged_count": len(merged_nodes),
        "compression_ratio": compression_ratio,
        "decisions_count": len(decisions)
    }


@router.get("/decisions")
async def get_decisions(db: AsyncSession = Depends(get_db)):
    """获取整合决策列表"""
    result = await db.execute(select(MergeDecision))
    decisions = result.scalars().all()
    return decisions
