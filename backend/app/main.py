from typing import List
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers import textbooks, graph, rag, chat
from app.database import init_db
from app.models import Textbook, Chapter, KnowledgeNode, KnowledgeEdge, MergeDecision, Chunk  # noqa: F401
from app.graph.workflow import workflow_app
from app.graph.state import GraphState

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(title="学科知识整合智能体 API", lifespan=lifespan)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(textbooks.router, prefix="/api/textbooks", tags=["教材管理"])
app.include_router(graph.router, prefix="/api/graph", tags=["知识图谱"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG问答"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])

@app.post("/api/pipeline/run")
async def run_pipeline(textbook_paths: List[str]):
    """运行完整流水线"""
    initial_state: GraphState = {
        "textbook_paths": textbook_paths,
        "textbooks": [],
        "chapters": [],
        "nodes": [],
        "edges": [],
        "merged_nodes": [],
        "merge_decisions": [],
        "current_state": "parse",
        "error": None,
        "progress": 0.0
    }

    final_state = await workflow_app.ainvoke(initial_state)

    return final_state

@app.get("/")
async def root():
    return {"message": "学科知识整合智能体 API"}
