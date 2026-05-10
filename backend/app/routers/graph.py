from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.knowledge import KnowledgeNode, KnowledgeEdge, MergeDecision
from app.models.chapter import Chapter
from app.services.extractor import extractor
from app.services.merger import merger

router = APIRouter()

@router.post("/extract/{textbook_id}")
async def extract_knowledge(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """提取教材知识点"""
    result = await db.execute(select(Chapter).where(Chapter.textbook_id == textbook_id))
    chapters = result.scalars().all()

    if not chapters:
        raise HTTPException(status_code=404, detail="未找到教材章节")

    all_nodes = []
    all_edges = []

    for chapter in chapters:
        if not chapter.content or not chapter.content.strip():
            continue

        nodes = await extractor.extract_from_chapter(
            chapter.content,
            textbook_id,
            chapter.chapter_id,
            chapter.page_start
        )
        all_nodes.extend(nodes)

        edges = await extractor.identify_relations(nodes)
        all_edges.extend(edges)

    for node in all_nodes:
        db.add(node)
    for edge in all_edges:
        db.add(edge)
    await db.commit()

    return {
        "textbook_id": textbook_id,
        "nodes_count": len(all_nodes),
        "edges_count": len(all_edges)
    }

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
