# AI Medical Consultant

基于 LLM + RAG + Agent 的智能医疗问诊系统

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.5-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> 本项目仅供学习和技术研究使用，AI 生成的医疗建议仅供参考，**不构成正式诊断**。如有不适请及时就医。

## 功能特性

- **智能问诊** — 多轮对话收集症状，AI 分析并给出分诊建议
- **RAG 检索增强** — 基于 FAISS 向量索引的医学知识库检索（支持稠密+稀疏混合检索）
- **Agent 决策编排** — 意图识别（问诊/查询/闲聊）→ 症状分析 → 追问 → 分诊 → 诊断
- **流式对话** — WebSocket 实时流式输出，逐 token 推送
- **知识库管理** — 支持手动添加、搜索、文档上传（PDF/Word/Markdown/TXT）
- **JWT 认证** — 用户注册/登录，会话隔离

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | FastAPI + Uvicorn |
| AI 模型 | DeepSeek Chat（兼容 OpenAI 接口） |
| Embedding | BAAI/bge-small-zh-v1.5 |
| 向量数据库 | FAISS |
| 关系数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 前端框架 | Vue 3 + Pinia + Element Plus |
| 构建工具 | Vite |
| 容器化 | Docker Compose |

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 克隆项目

```bash
git clone https://github.com/henrywang2001/ai-medical-consultant.git
cd ai-medical-consultant
```

### 2. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp backend/.env.example backend/.env
# 编辑 backend/.env，填入你的 API Key
```

| 配置项 | 说明 |
|--------|------|
| `LLM_API_KEY` | DeepSeek API Key |
| `LLM_BASE_URL` | API 地址（默认 `https://api.deepseek.com`） |
| `EMBEDDING_API_KEY` | 可选，DashScope API Key（本地模型自动降级） |

### 4. 初始化医学知识库

```bash
cd backend
py -m data.medical_kb.init_kb
```

### 5. 启动后端

```bash
py -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --reload
```

访问 http://localhost:9000/docs 查看 API 文档。

### 6. 启动前端（可选）

```bash
cd frontend
npm install
npm run dev
```

访问 http://localhost:5173（Vite 自动代理 API 请求到后端）。

### Docker 一键部署

```bash
docker compose up -d
docker compose exec backend python -m data.medical_kb.init_kb
```

## 项目结构

```
ai-medical-consultant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── models/
│   │   │   ├── database.py      # SQLAlchemy ORM
│   │   │   └── schemas.py       # Pydantic 数据模型
│   │   ├── routers/
│   │   │   ├── user.py          # 用户注册/登录
│   │   │   ├── consult.py       # 问诊会话管理
│   │   │   ├── agent.py         # Agent 分诊/诊断 API
│   │   │   ├── knowledge.py     # 知识库 CRUD + 检索
│   │   │   └── websocket.py     # WebSocket 流式对话
│   │   ├── services/
│   │   │   ├── agent_service.py # Agent 决策编排
│   │   │   ├── llm_service.py   # LLM 调用（流式/非流式）
│   │   │   └── rag_service.py   # RAG 检索增强
│   │   └── middleware/
│   │       └── auth.py          # JWT 认证
│   ├── data/medical_kb/
│   │   └── init_kb.py           # 知识库初始化（8 条示例医学知识）
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── views/               # 页面组件
│   │   │   ├── Home.vue         # 首页
│   │   │   ├── Login.vue        # 登录/注册
│   │   │   ├── Consult.vue      # 问诊对话
│   │   │   └── Knowledge.vue    # 知识库管理
│   │   ├── router/              # Vue Router
│   │   ├── stores/              # Pinia 状态管理
│   │   └── api/                 # Axios 封装
│   └── vite.config.js
└── docker-compose.yml
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/user/register` | 用户注册 |
| POST | `/api/v1/user/login` | 用户登录 |
| GET | `/api/v1/user/me` | 获取当前用户 |
| POST | `/api/v1/consult/` | 创建问诊会话 |
| GET | `/api/v1/consult/` | 问诊列表 |
| GET | `/api/v1/consult/{id}` | 问诊详情 |
| POST | `/api/v1/agent/triage` | Agent 分诊决策 |
| POST | `/api/v1/agent/diagnose` | Agent 诊断建议 |
| POST | `/api/v1/knowledge/documents` | 添加知识 |
| GET | `/api/v1/knowledge/documents` | 知识列表 |
| POST | `/api/v1/knowledge/search` | 知识检索 |
| POST | `/api/v1/knowledge/upload` | 上传文档 |
| GET | `/api/v1/knowledge/stats` | 知识库统计 |
| WS | `/api/ws/chat` | WebSocket 流式对话 |

## Agent 决策流程

```
用户输入 → 意图识别
              ├─ 问诊类: 症状分析 → 追问收集 → RAG检索 → LLM诊断 → 分诊建议
              ├─ 查询类: RAG检索 → LLM回答
              └─ 闲聊类: LLM直接回复
                        ↓
                  流式输出（WebSocket）
```

## License

MIT License
