# Frontend Components

四个核心组件构成主界面，对应赛题要求的左/中/右三栏布局。

| 组件 | 文件 | 职责 |
|------|------|------|
| TextbookPanel | `TextbookPanel.jsx` | 左侧教材管理。文件上传（拖拽+点选）、教材列表、解析状态、删除/重新解析操作 |
| GraphVisualization | `GraphVisualization.jsx` | 中间知识图谱。基于 ECharts 力导向图，节点点击详情、缩放拖拽、按教材着色、按出现频次缩放节点 |
| RAGPanel | `RAGPanel.jsx` | 右侧 RAG 问答。问题输入、回答展示、引用来源列表、相关度评分、原文 chunk 展开 |
| ChatPanel | `ChatPanel.jsx` | 右侧多轮对话。聊天界面、对话历史、意图识别、整合决策修改触发 |

## 数据流

所有组件通过 `services/api.js` 调用后端：

```
TextbookPanel  → POST /api/textbooks/upload + parse
                 触发 SSE 监听 /api/graph/extract/{id}/progress
GraphVisualization → GET /api/graph/nodes + /api/graph/edges
                     POST /api/graph/merge
RAGPanel       → POST /api/rag/index + /api/rag/query
                 GET  /api/rag/status
ChatPanel      → POST /api/chat/message
                 GET  /api/chat/history
```

## 状态管理

未引入 Redux/Zustand。状态通过 `App.jsx` 顶层 useState + props 下发，组件间通信（如教材选中→图谱刷新）通过回调上提。规模适配，未来超过 6 个组件可考虑引入 Zustand。

## 样式

- UI 库：Ant Design 5
- 主题：定制化深色背景（见 `styles/global.css`），`backdrop-filter: blur(10px)` 实现毛玻璃 tooltip
- 响应式：1920×1080 优化，未做移动端适配
