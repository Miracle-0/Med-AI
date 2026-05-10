import os
import uuid
from typing import List, Tuple
from datetime import datetime, timezone
import fitz  # PyMuPDF
from app.models.textbook import Textbook, ParseStatus
from app.models.chapter import Chapter


class TextbookParser:
    """教材解析器"""

    def __init__(self, upload_dir: str = "./uploads"):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)

    @staticmethod
    def now():
        return datetime.now(timezone.utc)

    async def save_file(self, file_content: bytes, filename: str) -> str:
        """保存上传的文件"""
        file_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{file_id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(file_content)
        return file_path

    async def parse_pdf(self, file_path: str, textbook_id: str) -> Tuple[Textbook, List[Chapter]]:
        """解析PDF文件"""
        doc = fitz.open(file_path)

        filename = os.path.basename(file_path)
        title = doc.metadata.get("title", filename.replace(".pdf", ""))
        total_pages = len(doc)

        textbook = Textbook(
            textbook_id=textbook_id,
            filename=filename,
            title=title,
            format="pdf",
            total_pages=total_pages,
            total_chars=0,
            upload_time=datetime.now(timezone.utc),
            parse_status=ParseStatus.PARSING
        )

        chapters = []
        current_chapter = None
        chapter_content = []
        chapter_start_page = 0
        chapter_id = 0

        for page_num in range(total_pages):
            page = doc[page_num]
            text = page.get_text()

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if self._is_chapter_title(line):
                    if current_chapter and chapter_content:
                        chapter_id += 1
                        content = "\n".join(chapter_content)
                        chapters.append(Chapter(
                            chapter_id=f"{textbook_id}_ch_{chapter_id:02d}",
                            textbook_id=textbook_id,
                            title=current_chapter,
                            page_start=chapter_start_page,
                            page_end=page_num,
                            content=content,
                            char_count=len(content)
                        ))

                    current_chapter = line
                    chapter_content = []
                    chapter_start_page = page_num + 1
                else:
                    chapter_content.append(line)

        if current_chapter and chapter_content:
            chapter_id += 1
            content = "\n".join(chapter_content)
            chapters.append(Chapter(
                chapter_id=f"{textbook_id}_ch_{chapter_id:02d}",
                textbook_id=textbook_id,
                title=current_chapter,
                page_start=chapter_start_page,
                page_end=total_pages,
                content=content,
                char_count=len(content)
            ))

        textbook.total_chars = sum(ch.char_count for ch in chapters)
        textbook.parse_status = ParseStatus.COMPLETED

        doc.close()
        return textbook, chapters

    async def parse_markdown(self, file_path: str, textbook_id: str) -> Tuple[Textbook, List[Chapter]]:
        """解析Markdown文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(file_path)
        title = filename.replace(".md", "")

        chapters = []
        current_chapter = None
        chapter_content = []
        chapter_id = 0

        for line in content.split("\n"):
            if line.startswith("# ") or line.startswith("## "):
                if current_chapter and chapter_content:
                    chapter_id += 1
                    ch_content = "\n".join(chapter_content)
                    chapters.append(Chapter(
                        chapter_id=f"{textbook_id}_ch_{chapter_id:02d}",
                        textbook_id=textbook_id,
                        title=current_chapter,
                        page_start=1,
                        page_end=1,
                        content=ch_content,
                        char_count=len(ch_content)
                    ))

                current_chapter = line.lstrip("# ").strip()
                chapter_content = []
            else:
                chapter_content.append(line)

        if current_chapter and chapter_content:
            chapter_id += 1
            ch_content = "\n".join(chapter_content)
            chapters.append(Chapter(
                chapter_id=f"{textbook_id}_ch_{chapter_id:02d}",
                textbook_id=textbook_id,
                title=current_chapter,
                page_start=1,
                page_end=1,
                content=ch_content,
                char_count=len(ch_content)
            ))

        total_chars = sum(ch.char_count for ch in chapters)

        textbook = Textbook(
            textbook_id=textbook_id,
            filename=filename,
            title=title,
            format="md",
            total_pages=1,
            total_chars=total_chars,
            upload_time=datetime.now(timezone.utc),
            parse_status=ParseStatus.COMPLETED
        )

        return textbook, chapters

    async def parse_text(self, file_path: str, textbook_id: str) -> Tuple[Textbook, List[Chapter]]:
        """解析TXT文件"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(file_path)
        title = filename.replace(".txt", "")

        chapters = []
        paragraphs = content.split("\n\n")
        chapter_id = 0

        for i, para in enumerate(paragraphs):
            if para.strip():
                chapter_id += 1
                chapters.append(Chapter(
                    chapter_id=f"{textbook_id}_ch_{chapter_id:02d}",
                    textbook_id=textbook_id,
                    title=f"第{chapter_id}部分",
                    page_start=1,
                    page_end=1,
                    content=para.strip(),
                    char_count=len(para.strip())
                ))

        total_chars = sum(ch.char_count for ch in chapters)

        textbook = Textbook(
            textbook_id=textbook_id,
            filename=filename,
            title=title,
            format="txt",
            total_pages=1,
            total_chars=total_chars,
            upload_time=datetime.now(timezone.utc),
            parse_status=ParseStatus.COMPLETED
        )

        return textbook, chapters

    def _is_chapter_title(self, line: str) -> bool:
        """检测是否为章节标题"""
        import re
        patterns = [
            r"^第[一二三四五六七八九十\d]+章",
            r"^Chapter\s+\d+",
            r"^CHAPTER\s+\d+",
        ]
        for pattern in patterns:
            if re.match(pattern, line):
                return True
        return False


parser = TextbookParser()
