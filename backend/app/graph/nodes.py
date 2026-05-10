from app.graph.state import GraphState, PipelineState
from app.services.parser import parser
from app.services.extractor import extractor

async def parse_node(state: GraphState) -> GraphState:
    """解析教材文件"""
    try:
        textbooks = []
        chapters = []

        for path in state["textbook_paths"]:
            if path.endswith(".pdf"):
                textbook, book_chapters = await parser.parse_pdf(path, f"book_{len(textbooks)}")
            elif path.endswith(".md"):
                textbook, book_chapters = await parser.parse_markdown(path, f"book_{len(textbooks)}")
            elif path.endswith(".txt"):
                textbook, book_chapters = await parser.parse_text(path, f"book_{len(textbooks)}")
            else:
                continue

            textbooks.append({
                "textbook_id": textbook.textbook_id,
                "filename": textbook.filename,
                "title": textbook.title,
                "format": textbook.format,
                "total_pages": textbook.total_pages,
                "total_chars": textbook.total_chars
            })
            chapters.extend([{
                "chapter_id": ch.chapter_id,
                "textbook_id": ch.textbook_id,
                "title": ch.title,
                "page_start": ch.page_start,
                "page_end": ch.page_end,
                "content": ch.content,
                "char_count": ch.char_count
            } for ch in book_chapters])

        return {
            **state,
            "textbooks": textbooks,
            "chapters": chapters,
            "current_state": PipelineState.EXTRACT.value,
            "progress": 0.3
        }
    except Exception as e:
        return {
            **state,
            "error": str(e),
            "current_state": "error"
        }

async def extract_node(state: GraphState) -> GraphState:
    """提取知识点"""
    try:
        nodes = []
        edges = []

        for chapter in state["chapters"]:
            chapter_nodes = await extractor.extract_from_chapter(
                chapter["content"],
                chapter["textbook_id"],
                chapter["chapter_id"],
                chapter["page_start"]
            )
            nodes.extend([{
                "node_id": node.node_id,
                "name": node.name,
                "definition": node.definition,
                "category": node.category,
                "textbook_id": node.textbook_id,
                "chapter_id": node.chapter_id,
                "page": node.page
            } for node in chapter_nodes])

            chapter_edges = await extractor.identify_relations(chapter_nodes)
            edges.extend([{
                "edge_id": edge.edge_id,
                "source_node_id": edge.source_node_id,
                "target_node_id": edge.target_node_id,
                "relation_type": edge.relation_type,
                "description": edge.description
            } for edge in chapter_edges])

        return {
            **state,
            "nodes": nodes,
            "edges": edges,
            "current_state": PipelineState.MERGE.value,
            "progress": 0.6
        }
    except Exception as e:
        return {
            **state,
            "error": str(e),
            "current_state": "error"
        }

async def merge_node(state: GraphState) -> GraphState:
    """整合知识点"""
    try:
        return {
            **state,
            "merged_nodes": state["nodes"],
            "merge_decisions": [],
            "current_state": PipelineState.DONE.value,
            "progress": 1.0
        }
    except Exception as e:
        return {
            **state,
            "error": str(e),
            "current_state": "error"
        }
