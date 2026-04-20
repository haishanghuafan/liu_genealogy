# 族谱云 - 刘氏乾正公族谱管理系统

> 基于 Next.js 15 + FastAPI 的现代化多租户族谱管理系统，支持族谱树可视化、成员管理、多租户隔离

## 🏗️ 项目结构

```
.
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/        # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── middleware/    # 中间件
│   │   ├── models/        # 数据模型
│   │   ├── services/      # 业务服务
│   │   └── main.py        # 应用入口
│   └── tests/             # 测试
│
├── frontend/              # Next.js 前端
│   ├── app/              # 页面路由
│   ├── components/       # UI 组件
│   └── lib/               # 工具库
│
├── docker/               # Docker 配置
├── docs/                 # 文档（原始族谱资料）
└── scripts/              # 工具脚本
```

## 🚀 快速开始

### 前置要求
- Python 3.11+
- Node.js 18+
- pnpm (推荐) 或 npm

### 启动后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API 文档：http://localhost:8000/api/v1/docs

### 启动前端

```bash
cd frontend
pnpm install
pnpm dev
```

访问：http://localhost:3000

### Docker 部署

```bash
docker-compose up -d
```

## 📚 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 15, React 18, TypeScript 5, Tailwind CSS, shadcn/ui, TanStack Query |
| 后端 | FastAPI 0.115, SQLAlchemy 2.0 (Async), Pydantic v2 |
| 数据库 | SQLite3 (开发), PostgreSQL 16 (生产) |
| 认证 | JWT |
| 图表 | D3.js, react-d3-tree |
| 部署 | Docker, Nginx, Gunicorn |

## ✅ 功能特性

### 核心功能
- ✅ 用户认证（注册/登录/修改密码）
- ✅ 多租户系统
- ✅ 人物管理（CRUD）
- ✅ 家族树可视化
- ✅ 支系管理
- ✅ 世代管理
- ✅ 配偶关系管理
- ✅ 搜索功能
- ✅ Excel 数据导入/导出
- ✅ 文件管理

### 前端页面
- `/login` - 用户登录
- `/register` - 用户注册
- `/t/[tenant]` - 租户首页
- `/t/[tenant]/persons` - 人物列表
- `/t/[tenant]/family-tree` - 族谱树
- `/t/[tenant]/branches` - 支系列表
- `/t/[tenant]/generations` - 世代列表
- `/t/[tenant]/import` - 数据导入
- `/t/[tenant]/export` - 数据导出
- `/t/[tenant]/analytics` - 统计分析
- `/t/[tenant]/settings` - 租户设置

## 📁 项目结构详情

### 后端 (backend/app/)

```
api/v1/endpoints/          # API 端点
├── auth.py               # 认证
├── persons.py            # 人物管理
├── families.py           # 家族关系
├── branches.py           # 支系管理
├── generations.py        # 世代管理
├── family_tree.py        # 族谱树
├── search.py             # 搜索
├── import_data.py        # 数据导入
├── export.py             # 数据导出
├── files.py              # 文件管理
├── tenants.py            # 租户管理
└── subscriptions.py      # 订阅管理

models/                   # 数据模型
├── tenant.py            # 租户模型
├── system.py            # 系统模型
├── analytics.py         # 统计模型
└── records.py           # 记录模型

services/                 # 业务服务
├── auth_service.py      # 认证服务
├── family_service.py    # 族谱服务
├── excel_import_service.py  # Excel导入
├── export_service.py    # 导出服务
├── neo4j_service.py     # Neo4j图数据库
└── visit_tracker.py     # 访问统计
```

### 前端 (frontend/)

```
app/
├── [tenant]/            # 租户路由
│   ├── persons/        # 人物页面
│   ├── family-tree/    # 族谱树
│   ├── branches/       # 支系
│   ├── generations/    # 世代
│   ├── import/         # 导入
│   ├── export/         # 导出
│   └── analytics/      # 统计
│
├── t/[tenant]/         # 租户管理页面
│   ├── members/        # 成员管理
│   ├── persons/        # 人物管理
│   └── subscription/  # 订阅
│
components/
├── ui/                 # shadcn/ui 组件
├── family-tree/        # 族谱树组件
└── admin/              # 管理组件
```

## � 环境变量

### 后端 (.env)
```
DATABASE_URL=sqlite+aiosqlite:///./genealogy.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 前端 (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## 📖 文档

项目文档位于 `AGENTS.md`，包含：
- 开发规范
- 代码风格
- AI 生成规则
- 优化工作指南

## 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/ -v

# 前端构建检查
cd frontend
pnpm build
```

## � 许可证

私有项目
