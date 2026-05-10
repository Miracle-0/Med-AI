from fastapi import APIRouter

router = APIRouter()

@router.post("/build")
async def build_graph():
    """构建知识图谱"""
    return {"message": "TODO: 实现知识图谱构建"}

@router.get("/query")
async def query_graph():
    """查询知识图谱"""
    return {"message": "TODO: 实现知识图谱查询"}
