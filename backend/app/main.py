from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import textbooks, graph, rag, chat

app = FastAPI(title="学科知识整合智能体 API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(textbooks.router, prefix="/api/textbooks", tags=["教材管理"])
app.include_router(graph.router, prefix="/api/graph", tags=["知识图谱"])
app.include_router(rag.router, prefix="/api/rag", tags=["RAG问答"])
app.include_router(chat.router, prefix="/api/chat", tags=["对话"])

@app.get("/")
async def root():
    return {"message": "学科知识整合智能体 API"}
