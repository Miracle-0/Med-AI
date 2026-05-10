import pytest
from app.services.rag_service import RAGService

@pytest.fixture
def rag_service():
    return RAGService()

@pytest.mark.asyncio
async def test_rag_query_empty(rag_service):
    """测试空知识库查询"""
    answer, chunks = await rag_service.query("什么是炎症？")
    assert "知识库为空" in answer
    assert len(chunks) == 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
