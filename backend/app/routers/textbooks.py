import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.textbook import Textbook, ParseStatus
from app.models.chapter import Chapter
from app.services.parser import parser

router = APIRouter()


@router.post("/upload")
async def upload_textbook(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """上传教材文件（仅保存，不解析）"""
    allowed_formats = [".pdf", ".md", ".txt"]
    file_ext = "." + file.filename.split(".")[-1].lower()
    if file_ext not in allowed_formats:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")

    textbook_id = f"book_{str(uuid.uuid4())[:8]}"
    file_content = await file.read()
    file_path = await parser.save_file(file_content, file.filename)

    # 创建教材记录（状态为 uploaded，等待解析）
    title = file.filename.rsplit(".", 1)[0]
    textbook = Textbook(
        textbook_id=textbook_id,
        filename=file.filename,
        title=title,
        format=file_ext.lstrip("."),
        total_pages=0,
        total_chars=0,
        upload_time=parser.now(),
        parse_status=ParseStatus.UPLOADED
    )
    db.add(textbook)
    await db.commit()

    return {
        "textbook_id": textbook_id,
        "filename": file.filename,
        "status": "uploaded"
    }


@router.post("/{textbook_id}/parse")
async def parse_textbook(
    textbook_id: str,
    db: AsyncSession = Depends(get_db)
):
    """解析已上传的教材文件"""
    result = await db.execute(select(Textbook).where(Textbook.textbook_id == textbook_id))
    textbook = result.scalar_one_or_none()
    if not textbook:
        raise HTTPException(status_code=404, detail="教材不存在")

    # 查找文件
    import glob
    import os
    pattern = os.path.join(parser.upload_dir, f"*{textbook.filename}")
    matches = glob.glob(pattern)
    if not matches:
        raise HTTPException(status_code=404, detail="文件不存在，请重新上传")

    file_path = matches[0]
    file_ext = "." + textbook.filename.split(".")[-1].lower()

    try:
        textbook.parse_status = ParseStatus.PARSING
        await db.commit()

        if file_ext == ".pdf":
            _, chapters = await parser.parse_pdf(file_path, textbook_id)
        elif file_ext == ".md":
            _, chapters = await parser.parse_markdown(file_path, textbook_id)
        elif file_ext == ".txt":
            _, chapters = await parser.parse_text(file_path, textbook_id)
        else:
            raise HTTPException(status_code=400, detail="不支持的文件格式")

        # 更新教材信息
        textbook.total_pages = chapters[-1].page_end if chapters else 0
        textbook.total_chars = sum(ch.char_count for ch in chapters)
        textbook.parse_status = ParseStatus.COMPLETED

        db.add(textbook)
        for chapter in chapters:
            db.add(chapter)
        await db.commit()

        return {
            "textbook_id": textbook_id,
            "status": "completed",
            "chapters_count": len(chapters),
            "total_chars": textbook.total_chars
        }
    except Exception as e:
        textbook.parse_status = ParseStatus.FAILED
        await db.commit()
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.get("/")
async def list_textbooks(db: AsyncSession = Depends(get_db)):
    """获取教材列表"""
    result = await db.execute(select(Textbook))
    textbooks = result.scalars().all()
    return textbooks


@router.get("/{textbook_id}")
async def get_textbook(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """获取教材详情"""
    result = await db.execute(select(Textbook).where(Textbook.textbook_id == textbook_id))
    textbook = result.scalar_one_or_none()
    if not textbook:
        raise HTTPException(status_code=404, detail="教材不存在")
    return textbook


@router.get("/{textbook_id}/chapters")
async def get_textbook_chapters(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """获取教材章节列表"""
    result = await db.execute(select(Chapter).where(Chapter.textbook_id == textbook_id))
    chapters = result.scalars().all()
    return chapters


@router.delete("/{textbook_id}")
async def delete_textbook(textbook_id: str, db: AsyncSession = Depends(get_db)):
    """删除教材"""
    result = await db.execute(select(Textbook).where(Textbook.textbook_id == textbook_id))
    textbook = result.scalar_one_or_none()
    if not textbook:
        raise HTTPException(status_code=404, detail="教材不存在")

    await db.delete(textbook)
    await db.commit()
    return {"message": "删除成功"}
