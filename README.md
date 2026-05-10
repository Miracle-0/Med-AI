# 学科知识整合智能体

基于 LangGraph + RAG 的学科知识整合智能体，能够自动解析教材内容，构建跨学科知识图谱，并提供智能问答服务。

## 功能特性

- **教材解析**: 支持 PDF、DOCX 格式的教材内容自动解析
- **知识图谱**: 自动提取知识点，构建跨学科关联图谱
- **RAG 问答**: 基于教材内容的智能问答系统
- **可视化**: ECharts 驱动的交互式知识图谱展示

## 技术栈

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **LangGraph**: 基于 LangChain 的图执行框架
- **FAISS**: 向量相似度检索
- **SQLAlchemy**: 异步数据库 ORM

### 前端
- **React 18**: 用户界面框架
- **ECharts 5**: 数据可视化库
- **Ant Design**: UI 组件库
- **Vite**: 构建工具

## 快速开始

### 环境要求
- Python 3.10+
- Node.js 18+
- npm 或 yarn

### 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 OpenAI API Key

# 启动服务
python run.py
```

后端服务将在 http://localhost:8000 启动

### 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端应用将在 http://localhost:3000 启动

## 配置说明

### 环境变量 (.env)

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4

# Embedding 模型
EMBEDDING_MODEL=text-embedding-ada-002
```

## 项目结构

```
学科知识整合智能体/
├── backend/
│   ├── app/
│   │   ├── routers/          # API 路由
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 应用入口
│   │   └── config.py        # 配置管理
│   ├── data/
│   │   └── textbooks/       # 教材存储目录
│   ├── uploads/             # 上传文件目录
│   ├── requirements.txt     # Python 依赖
│   └── run.py              # 启动脚本
├── frontend/
│   ├── src/                 # React 源代码
│   ├── public/              # 静态资源
│   ├── package.json         # 前端依赖
│   └── vite.config.js       # Vite 配置
├── .gitignore
└── README.md
```

## API 文档

启动后端服务后，访问 http://localhost:8000/docs 查看 Swagger API 文档。

### 主要 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/textbooks/upload` | POST | 上传教材 |
| `/api/textbooks/list` | GET | 获取教材列表 |
| `/api/graph/build` | POST | 构建知识图谱 |
| `/api/graph/query` | GET | 查询知识图谱 |
| `/api/rag/query` | POST | RAG 问答 |
| `/api/chat/send` | POST | 发送对话消息 |

## 许可证

MIT License
