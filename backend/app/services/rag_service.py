import os
import uuid
from typing import List, Dict, Tuple
import faiss
import numpy as np
from app.models.rag import Chunk
from app.models.chapter import Chapter
from app.services.llm_service import llm_service
from app.utils.embedding import embedding_service
from app.utils.text_processing import chunk_text
from app.config import settings

class RAGService:
    """RAG服务"""

    def __init__(self):
        self.index = None
        self.chunks: List[Chunk] = []
        self.dimension = 1536

    async def build_index(self, chapters: List[Chapter], textbook_id: str) -> int:
        """构建向量索引"""
        all_chunks = []

        for chapter in chapters:
            text_chunks = chunk_text(chapter.content, chunk_size=600, overlap=100)

            for i, chunk_content in enumerate(text_chunks):
                chunk = Chunk(
                    chunk_id=f"{textbook_id}_chunk_{str(uuid.uuid4())[:8]}",
                    textbook_id=textbook_id,
                    chapter_id=chapter.chapter_id,
                    page=chapter.page_start,
                    content=chunk_content
                )
                all_chunks.append(chunk)

        texts = [chunk.content for chunk in all_chunks]
        embeddings = await embedding_service.get_embeddings(texts)

        self.dimension = len(embeddings[0])
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings).astype('float32'))

        self.chunks = all_chunks

        os.makedirs(os.path.dirname(settings.FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, settings.FAISS_INDEX_PATH)

        return len(all_chunks)

    async def load_index(self) -> bool:
        """加载索引"""
        if os.path.exists(settings.FAISS_INDEX_PATH):
            self.index = faiss.read_index(settings.FAISS_INDEX_PATH)
            return True
        return False

    async def query(self, question: str, top_k: int = 5) -> Tuple[str, List[Dict]]:
        """查询并生成回答"""
        if self.index is None:
            await self.load_index()

        if self.index is None or self.index.ntotal == 0:
            return "知识库为空，请先建立索引", []

        query_embedding = await embedding_service.get_embedding(question)
        query_vector = np.array([query_embedding]).astype('float32')

        distances, indices = self.index.search(query_vector, top_k)

        relevant_chunks = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.chunks):
                chunk = self.chunks[idx]
                relevant_chunks.append({
                    "content": chunk.content,
                    "textbook_id": chunk.textbook_id,
                    "chapter_id": chunk.chapter_id,
                    "page": chunk.page,
                    "relevance_score": float(1 / (1 + distances[0][i]))
                })

        context = "\n\n".join([chunk["content"] for chunk in relevant_chunks])

        system_prompt = """你是一个学科知识整合助手。基于以下教材内容回答用户问题。

要求：
1. 只基于提供的上下文回答，不使用自身知识
2. 每个回答必须附带来源引用，格式为 [教材名称, 第X章, 第X页]
3. 如果上下文中找不到答案，回复"当前知识库中未找到相关信息"
4. 回答要准确、简洁、专业"""

        prompt = f"""上下文：
{context}

用户问题：{question}

请回答："""

        answer = await llm_service.generate(prompt, system_prompt)

        return answer, relevant_chunks

    def get_status(self) -> Dict:
        """获取索引状态"""
        return {
            "indexed_chunks": self.index.ntotal if self.index else 0,
            "dimension": self.dimension
        }

rag_service = RAGService()
