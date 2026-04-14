# 族谱云 - Next.js 多租户族谱系统

> 基于 Next.js 14 + FastAPI 的现代化族谱管理系统，支持族谱树可视化、成员管理、多租户隔离

**🎉 Next.js 迁移已完成 80%！Django 旧版本已删除**

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
│   └── requirements.txt   # Python 依赖
│
├── frontend/              # Next.js 前端
│   ├── app/              # 页面路由
│   ├── components/       # UI 组件
│   ├── lib/              # 工具库
│   └── public/           # 静态资源
│
├── docker/               # Docker 配置
├── scripts/              # 脚本工具
├── docs/                 # 文档
└── start-nextjs.sh       # 快速启动脚本
```

## 🚀 快速开始

### 方式一：使用启动脚本（推荐）

**一键启动前后端服务！**

```bash
./start-nextjs.sh
```

访问：
- 前端：http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档：http://localhost:8000/api/v1/docs

### 方式二：手动启动

```bash
# 后端
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite+aiosqlite:///./genealogy.db"
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

### 方式三：Docker Compose

```bash
# 开发环境
docker-compose up -d

# 生产环境
cp .env.production .env
docker-compose -f docker-compose.prod.yml up -d
```

### 环境要求

| 方式 | 必需 |
|------|------|
| 本地开发 | Python 3.11+, Node.js 18+ |
| Docker | Docker & Docker Compose |
| 生产环境 | PostgreSQL 16 (可选，默认 SQLite) |

**SQLite 默认启用，无需安装额外数据库！**

## 📚 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 14, React 18, TypeScript 5, Tailwind CSS, shadcn/ui |
| 后端 | FastAPI 0.115, SQLAlchemy 2.0 (Async), Pydantic v2 |
| 数据库 | SQLite3 (默认), PostgreSQL 16 (生产可选) |
| 认证 | JWT (PyJWT), bcrypt 密码加密 |
| 部署 | Docker, Nginx, Gunicorn |

## 🚢 部署

### 一键部署

```bash
chmod +x deploy.sh
./deploy.sh production
```

### 手动部署

1. 复制 `.env.production` 为 `.env` 并配置
2. 配置 SSL 证书到 `docker/nginx/ssl/`
3. 运行 `docker-compose -f docker-compose.prod.yml up -d`
4. 运行数据库迁移 `alembic upgrade head`

详细部署指南：[部署文档](docs/DEPLOYMENT.md)

## ✅ 功能特性

### 已完成 (80%)
- ✅ 用户认证（注册/登录/密码修改）
- ✅ 多租户系统
- ✅ 人物管理（CRUD）
- ✅ 家族树可视化
- ✅ 支系管理
- ✅ 世代管理
- ✅ 配偶关系管理
- ✅ 基础搜索

### 待完成 (20%)
- ⏳ Excel 数据导入
- ⏳ 访问统计
- ⏳ 文件上传优化
- ⏳ 高级搜索

## 📖 文档

- [迁移完成总结](./MIGRATION_COMPLETE_SUMMARY.md)
- [迁移状态详情](./MIGRATION_STATUS.md)
- [测试清单](./NEXTJS_TEST_CHECKLIST.md)

- [架构设计文档](docs/ARCHITECTURE.md)
- [API 文档](http://localhost:8010/api/v1/docs)

## 🧪 测试

```bash
# 后端测试
cd backend
pytest tests/ -v --cov

# 前端测试
cd frontend
npm run test
```

## 📝 开发进度

- [x] 架构设计文档
- [x] 项目骨架搭建
- [x] 数据模型设计
- [x] 租户中间件
- [x] 认证系统
- [x] 族谱树可视化
- [x] 人物管理 API
- [x] 管理后台
- [x] 前端页面
- [x] 测试用例
- [x] 部署配置

## 📄 License

MIT
