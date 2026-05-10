import pytest
import os
import tempfile
from app.services.parser import TextbookParser


@pytest.fixture
def parser():
    return TextbookParser(upload_dir=tempfile.mkdtemp())


@pytest.mark.asyncio
async def test_parse_markdown(parser):
    """测试Markdown解析"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write("# 第一章 绪论\n\n这是第一章的内容。\n\n## 1.1 背景\n\n这是背景介绍。\n\n# 第二章 方法\n\n这是第二章的内容。")
        temp_path = f.name

    try:
        textbook, chapters = await parser.parse_markdown(temp_path, "test_01")
        assert textbook.title == "test_01"
        assert len(chapters) >= 1
        assert chapters[0].title is not None
    finally:
        os.unlink(temp_path)


@pytest.mark.asyncio
async def test_parse_text(parser):
    """测试TXT解析"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("这是第一段内容。\n\n这是第二段内容。\n\n这是第三段内容。")
        temp_path = f.name

    try:
        textbook, chapters = await parser.parse_text(temp_path, "test_02")
        assert textbook.title == "test_02"
        assert len(chapters) >= 1
    finally:
        os.unlink(temp_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
