# 族谱云 - AI 助手指南

## 项目概述

多租户族谱管理系统，基于 Next.js 15 + FastAPI 构建，支持族谱树可视化、成员管理、数据导入导出。

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 15, React 18, TypeScript 5, Tailwind CSS, shadcn/ui |
| 后端 | FastAPI 0.115, SQLAlchemy 2.0 (Async), Pydantic v2 |
| 数据库 | SQLite3 (开发), PostgreSQL 16 (生产) |
| 端口 | 前端 3012, 后端 8012 |

## 行为边界

### ✅ 可以做

- 修改 `frontend/app/` 和 `frontend/components/` 下的文件
- 修改 `backend/app/` 下的业务逻辑
- 创建新的 API 端点和页面组件
- 重构现有代码改善性能

### ❌ 不能做

- 删除 `docs/刘氏族谱资料/` 下的原始数据
- 修改 `docker/` 下的生产配置
- 直接修改数据库（必须通过迁移）
- 引入新依赖（需确认）

### ⚠️ 先问再做

- 删除任何文件
- 修改 `package.json` 或 `requirements.txt`
- 运行全量构建命令
- 修改环境变量配置

## 编码规范

### 前端 (TypeScript/Next.js)

```
路由: /t/[tenant]/xxx/page.tsx
组件: PascalCase，如 FamilyTreePage
工具: camelCase，如 fetchPersons
样式: Tailwind 类名，禁止行内 style
合并类名: cn()
状态: TanStack Query (服务端), useState (客户端)
```

### 后端 (Python/FastAPI)

```
路径: kebab-case，如 /family-tree
函数: snake_case，如 get_person_by_id
类型: 必须使用类型注解
异步: async def
响应: {"data": ..., "message": "success"}
```

### 禁止事项

- 禁止 `console.log`，使用日志
- 禁止 `print`，使用 `logging`
- 禁止 bare `except`，必须指定异常类型
- 禁止在模板中写复杂逻辑

## 常用命令

### 开发环境

```bash
# 后端
cd backend
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8012

# 前端
cd frontend
pnpm install
pnpm dev
```

### 生产环境

```bash
docker-compose up -d
```

## 文件结构

```
backend/app/
├── api/v1/endpoints/   # API 端点
├── core/               # 配置
├── middleware/         # 中间件
├── models/             # 数据模型
└── services/          # 业务服务

frontend/app/
├── [tenant]/           # 租户页面
│   ├── persons/
│   ├── family-tree/
│   └── ...
├── t/[tenant]/         # 管理页面
└── components/         # 组件
    ├── ui/            # shadcn/ui
    └── family-tree/   # 族谱树
```

## 测试要求

- 工具函数必须写单元测试
- API 端点必须写集成测试
- 测试命令: `pytest tests/ -v`
- 覆盖率目标: >80%

## 数据规则

### 族谱关系

- 父子关系: `father_id`, `mother_id` 外键
- 配偶关系: SpouseRelation 中间表
- 禁止用字符串存储关系

### 文件限制

| 类型 | 大小 | 格式 |
|------|------|------|
| 头像 | 5MB | JPG, PNG, GIF, WebP |
| 族谱图 | 10MB | JPG, PNG, PDF |
| 视频 | 100MB | MP4, AVI, MOV |

## 安全

- 密码: bcrypt 加密
- JWT: HS256，过期时间 30 分钟
- 输入: Pydantic 模型验证
- SQL: SQLAlchemy ORM（防注入）
- 敏感操作: 需要认证
