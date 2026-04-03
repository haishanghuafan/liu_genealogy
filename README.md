# 族谱云 - 多租户族谱 SaaS 平台

> 现代化的多家族族谱管理系统，支持族谱树可视化、成员管理、历史记录

## 🏗️ 项目结构

```
.
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── middleware/    # 中间件
│   │   ├── models/        # 数据模型
│   │   └── main.py        # 应用入口
│   ├── migrations/        # 数据库迁移
│   └── tests/             # 测试
│
├── frontend/              # Next.js 前端
│   ├── app/              # 页面
│   ├── components/       # 组件
│   └── lib/              # 工具库
│
├── docker/               # Docker 配置
├── scripts/              # 脚本工具
└── docs/                 # 文档
```

## 🚀 快速开始

### 方式一：本地开发（最简单）

**只需 Python + Node.js，使用 SQLite 数据库！**

```bash
# Windows
.\setup.ps1      # 安装依赖
.\start-dev.ps1  # 启动服务

# macOS/Linux
./setup.sh && ./start-dev.sh
```

访问：
- 前端: http://localhost:3010
- 后端 API: http://localhost:8010
- API 文档: http://localhost:8010/api/v1/docs

详细说明: [本地开发指南](docs/LOCAL_DEVELOPMENT.md)

### 方式二：Docker Compose

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
| 生产环境 | PostgreSQL 16, Neo4j 5 (可选) |

**SQLite 默认启用，无需安装额外数据库！**

## 📚 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Next.js 15, React 19, Tailwind CSS |
| 后端 | FastAPI, SQLAlchemy 2.0 |
| 数据库 | PostgreSQL 16, Neo4j 5 |
| 缓存 | Redis 7 |
| 搜索 | Meilisearch |
| 存储 | MinIO (S3 兼容) |

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

## 📖 文档

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
