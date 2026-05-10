import logging
from typing import List, Dict, Any
from app.graph.state import GraphState, PipelineState
from app.services.parser import parser
from app.services.extractor import extractor
from app.services.merger import merger
from app.models.knowledge import KnowledgeNode

logger = logging.getLogger(__name__)


async def parse_node(state: GraphState) -> GraphState:
    """解析教材文件"""
    try:
        textbooks: List[Dict[str, Any]] = []
        chapters: List[Dict[str, Any]] = []

        for path in state["textbook_paths"]:
            if path.endswith(".pdf"):
                textbook, book_chapters = await parser.parse_pdf(path, f"book_{len(textbooks)}")
            elif path.endswith(".md"):
                textbook, book_chapters = await parser.parse_markdown(path, f"book_{len(textbooks)}")
            elif path.endswith(".txt"):
                textbook, book_chapters = await parser.parse_text(path, f"book_{len(textbooks)}")
            elif path.endswith(".docx"):
                textbook, book_chapters = await parser.parse_docx(path, f"book_{len(textbooks)}")
            else:
                continue

            textbooks.append({
                "textbook_id": textbook.textbook_id,
                "filename": textbook.filename,
                "title": textbook.title,
                "format": textbook.format,
                "total_pages": textbook.total_pages,
                "total_chars": textbook.total_chars,
            })
            chapters.extend([{
                "chapter_id": ch.chapter_id,
                "textbook_id": ch.textbook_id,
                "title": ch.title,
                "page_start": ch.page_start,
                "page_end": ch.page_end,
                "content": ch.content,
                "char_count": ch.char_count,
            } for ch in book_chapters])

        return {
            **state,
            "textbooks": textbooks,
            "chapters": chapters,
            "current_state": PipelineState.EXTRACT.value,
            "progress": 0.3,
        }
    except Exception as e:
        logger.error(f"解析失败: {e}")
        return {**state, "error": str(e), "current_state": "error"}


async def extract_node(state: GraphState) -> GraphState:
    """提取知识点"""
    try:
        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []

        for chapter in state["chapters"]:
            if not chapter.get("content") or not chapter["content"].strip():
                continue

            chapter_nodes = await extractor.extract_from_chapter(
                chapter["content"],
                chapter["textbook_id"],
                chapter["chapter_id"],
                chapter["page_start"],
            )
            nodes.extend([{
                "node_id": node.node_id,
                "name": node.name,
                "definition": node.definition,
                "category": node.category,
                "textbook_id": node.textbook_id,
                "chapter_id": node.chapter_id,
                "page": node.page,
            } for node in chapter_nodes])

            chapter_edges = await extractor.identify_relations(chapter_nodes)
            edges.extend([{
                "edge_id": edge.edge_id,
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "relation_type": edge.relation_type,
                "description": edge.description,
            } for edge in chapter_edges])

        return {
            **state,
            "nodes": nodes,
            "edges": edges,
            "current_state": PipelineState.MERGE.value,
            "progress": 0.6,
        }
    except Exception as e:
        logger.error(f"提取失败: {e}")
        return {**state, "error": str(e), "current_state": "error"}


async def merge_node(state: GraphState) -> GraphState:
    """整合知识点 — 调用 merger 进行跨教材去重"""
    try:
        raw_nodes = state.get("nodes", [])
        if not raw_nodes:
            return {
                **state,
                "merged_nodes": [],
                "merge_decisions": [],
                "current_state": PipelineState.DONE.value,
                "progress": 1.0,
            }

        # 将 dict 转为 KnowledgeNode 对象
        node_objs = [
            KnowledgeNode(
                node_id=n["node_id"],
                name=n["name"],
                definition=n["definition"],
                category=n["category"],
                textbook_id=n["textbook_id"],
                chapter_id=n["chapter_id"],
                page=n["page"],
            )
            for n in raw_nodes
        ]

        # 查找重复组并执行合并
        duplicate_groups = await merger.find_duplicates(node_objs)
        merged_objs, decisions = await merger.execute_merge(node_objs, duplicate_groups)
        compression_ratio = merger.calculate_compression_ratio(node_objs, merged_objs)

        # 转回 dict
        merged_nodes = [{
            "node_id": n.node_id,
            "name": n.name,
            "definition": n.definition,
            "category": n.category,
            "textbook_id": n.textbook_id,
            "chapter_id": n.chapter_id,
            "page": n.page,
        } for n in merged_objs]

        merge_decisions = [{
            "decision_id": d.decision_id,
            "action": d.action.value if hasattr(d.action, 'value') else d.action,
            "affected_nodes": d.affected_nodes,
            "result_node_id": d.result_node_id,
            "reason": d.reason,
            "confidence": d.confidence,
        } for d in decisions]

        logger.info(
            f"整合完成: {len(node_objs)} → {len(merged_nodes)} 节点, "
            f"压缩比 {compression_ratio:.1%}, {len(decisions)} 条决策"
        )

        return {
            **state,
            "merged_nodes": merged_nodes,
            "merge_decisions": merge_decisions,
            "compression_ratio": compression_ratio,
            "current_state": PipelineState.DONE.value,
            "progress": 1.0,
        }
    except Exception as e:
        logger.error(f"整合失败: {e}")
        return {**state, "error": str(e), "current_state": "error"}
