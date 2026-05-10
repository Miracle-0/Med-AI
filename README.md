# 学科知识整合智能体

基于 LangGraph + RAG 的学科知识整合智能体，能够自动解析教材内容，构建跨学科知识图谱，并提供智能问答服务。

> 🚀 **一键启动**：`cp .env.example .env && docker-compose up -d` → 浏览器打开 http://localhost:3000

## 文档导航

- [需求分析](docs/需求分析.md) — 子问题分解与设计依据
- [系统设计](docs/系统设计.md) — 架构图、数据流、技术选型
- [Agent 架构说明](docs/Agent架构说明.md) — 核心评分文档
- [接口文档](docs/接口文档.md) — 完整 API 列表
- [RAG Benchmark](docs/RAG_Benchmark.md) — 自建评测集与实验数据
- [整合报告](report/整合报告.md) — 多教材整合实测报告

## 功能特性

- **教材解析**: 支持 PDF、Markdown、TXT 格式的教材内容自动解析
- **知识图谱**: 自动提取知识点，构建跨学科关联图谱，支持 4 种关系类型
- **跨教材整合**: 基于 Embedding 相似度检测重复知识点，LLM 自动决策合并/保留/删除
- **RAG 问答**: 基于教材内容的智能问答系统，附带引用来源和相关度评分
- **多轮对话**: 支持上下文的连续对话，帮助教师理解和优化整合方案
- **可视化**: ECharts 驱动的交互式知识图谱展示，支持缩放、拖拽、聚焦

## 技术栈

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **LangGraph**: 基于 LangChain 的图执行框架
- **FAISS**: 向量相似度检索
- **SQLAlchemy**: 异步数据库 ORM
- **PyMuPDF**: PDF 解析

### 前端
- **React 18**: 用户界面框架
- **ECharts 5**: 数据可视化库
- **Ant Design**: UI 组件库
- **Vite**: 构建工具

## Docker 一键部署（推荐）

```bash
# 1. 配置环境变量
cp backend/.env.example .env
# 编辑 .env 文件，填入 API Key

# 2. 启动服务
docker-compose up -d

# 3. 访问应用
# 前端: http://localhost:3000
# API 文档: http://localhost:8000/docs
```

环境变量说明：

| 变量 | 说明 | 示例 |
|------|------|------|
| `OPENAI_API_KEY` | LLM API 密钥 | `sk-xxx` |
| `OPENAI_BASE_URL` | LLM API 地址 | `https://api.gpugeek.com/v1` |
| `LLM_MODEL` | LLM 模型 ID | `Vendor2/Claude-4.7-opus` |
| `EMBEDDING_API_KEY` | Embedding API 密钥 | `ms-xxx` |
| `EMBEDDING_BASE_URL` | Embedding API 地址 | `https://api-inference.modelscope.cn/v1` |
| `EMBEDDING_MODEL` | Embedding 模型 ID | `Qwen/Qwen3-Embedding-8B` |

## 本地开发

### 环境要求
- Python 3.10+
- Node.js 18+

### 后端启动

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填入 API Key
python run.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 主要 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/textbooks/upload` | POST | 上传教材文件 |
| `/api/textbooks/{id}/parse` | POST | 解析已上传的教材 |
| `/api/textbooks/` | GET | 获取教材列表 |
| `/api/graph/extract/{id}` | POST | 提取知识点构建图谱 |
| `/api/graph/extract/{id}/progress` | GET | SSE 实时获取提取进度 |
| `/api/graph/nodes` | GET | 获取知识点列表 |
| `/api/graph/edges` | GET | 获取关系列表 |
| `/api/graph/merge` | POST | 跨教材知识点整合 |
| `/api/rag/index` | POST | 构建 RAG 向量索引 |
| `/api/rag/query` | POST | RAG 智能问答 |
| `/api/chat/message` | POST | 发送对话消息 |
| `/api/chat/history` | GET | 获取对话历史 |
| `/api/demo/load` | POST | 加载演示数据 |

## 项目结构

```
学科知识整合智能体/
├── backend/
│   ├── app/
│   │   ├── routers/          # API 路由 (textbooks, graph, rag, chat, demo)
│   │   ├── services/         # 业务逻辑 (parser, extractor, merger, llm, rag)
│   │   ├── models/           # 数据模型 (textbook, chapter, knowledge, rag)
│   │   ├── graph/            # LangGraph 状态机 (workflow, nodes, state)
│   │   ├── utils/            # 工具类 (embedding)
│   │   ├── main.py           # FastAPI 应用入口
│   │   ├── config.py         # 配置管理
│   │   └── database.py       # 数据库初始化
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── services/         # API 调用层
│   │   ├── styles/           # 全局样式
│   │   ├── App.jsx           # 主应用
│   │   └── main.jsx          # 入口
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── docs/                     # 设计文档
├── report/                   # 整合报告
└── test_data/                # 测试数据
```

## 许可证

MIT License
