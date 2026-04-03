# 本地开发环境搭建指南（无 Docker）

本文档介绍如何在没有 Docker 的情况下搭建本地开发环境。

## 🎉 最简开发配置

**只需要 Python + Node.js 即可开始开发！**

- ✅ 使用 SQLite（无需安装数据库）
- ✅ Neo4j、Redis、Meilisearch 都是可选的

---

## 1. 安装必要依赖

### 1.1 Python 3.11+

**Windows:**
1. 下载: https://www.python.org/downloads/
2. 安装时勾选 "Add Python to PATH"

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt install python3.11 python3.11-venv python3-pip
```

### 1.2 Node.js 18+

**Windows/macOS:**
下载: https://nodejs.org/

**Linux:**
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install nodejs
```

---

## 2. 快速启动（使用 SQLite）

### Windows

```powershell
# 1. 安装依赖
.\setup.ps1

# 2. 启动服务
.\start-dev.ps1
```

### macOS/Linux

```bash
# 1. 安装依赖
chmod +x setup.sh
./setup.sh

# 2. 启动服务
chmod +x start-dev.sh
./start-dev.sh
```

### 手动启动

```bash
# 后端
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# 前端 (新终端)
cd frontend
npm install
npm run dev
```

访问：
- 前端: http://localhost:3010
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/api/v1/docs

---

## 3. 数据库配置

### 3.1 SQLite（默认，推荐本地开发）

无需安装！项目默认使用 SQLite：

```env
# backend/.env
DATABASE_URL=sqlite+aiosqlite:///./genealogy.db
```

**多租户模式：**
- 系统数据库: `genealogy.db`
- 租户数据库: `tenants/{tenant_slug}.db`

### 3.2 PostgreSQL（生产环境推荐）

```env
# backend/.env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/genealogy
```

安装 PostgreSQL：
- Windows: https://www.postgresql.org/download/windows/
- macOS: `brew install postgresql@16`
- Linux: `sudo apt install postgresql-16`

---

## 4. 可选服务

### 4.1 Neo4j（族谱关系图查询）

用于高级图查询功能（如祖先链、后代链、血缘关系计算）。

**Windows:**
下载: https://neo4j.com/download/

**macOS:**
```bash
brew install neo4j
brew services start neo4j
```

**Linux:**
```bash
sudo apt install neo4j
sudo systemctl start neo4j
```

配置：
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
```

### 4.2 Redis（缓存）

用于 API 缓存、会话存储。

**Windows:**
- 下载: https://github.com/microsoftarchive/redis/releases
- 或使用 WSL

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux:**
```bash
sudo apt install redis-server
sudo systemctl start redis
```

配置：
```env
REDIS_URL=redis://localhost:6379/0
```

### 4.3 Meilisearch（全文搜索）

用于人物搜索功能。

**macOS:**
```bash
brew install meilisearch
meilisearch --master-key=masterKey
```

**Linux:**
```bash
curl -L https://install.meilisearch.com | sh
./meilisearch --master-key=masterKey
```

配置：
```env
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=masterKey
```

---

## 5. 数据库迁移

### SQLite（自动创建表）

SQLite 模式下，Alembic 迁移会自动创建表：

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### PostgreSQL

```bash
# 创建数据库
psql -U postgres -c "CREATE DATABASE genealogy;"

# 运行迁移
alembic upgrade head
```

---

## 6. API 功能模块

### 6.1 人物管理增强

**批量导入功能：**
- 支持 CSV 文件上传（UTF-8 / GBK 自动检测）
- 提供模板下载
- 预览前 5 行数据
- 错误汇总报告

**完整字段支持（28 个）：**
- 基本信息：姓名、字、号、别名、辈分字、外姓标记
- 生卒信息：年、地、农历生日
- 安葬信息：地点、风水坐向、朝向
- 传记信息：生平、成就、后人分布、备注

### 6.2 配偶关系类型（9 种）

| 类型 | 说明 |
|------|------|
| marriage | 婚姻（正室）|
| concubine | 妾室 |
| adopted | 继配 |
| zhuazhui | 招赘 |
| first-fifth | 一至五房 |

### 6.3 订阅套餐（4 级）

| 套餐 | 价格 | 人物上限 | 成员上限 | 存储 | 导出 |
|------|------|----------|----------|------|------|
| 免费版 | ¥0 | 100 | 5 | 100MB | ❌ |
| 基础版 | ¥99/年 | 500 | 20 | 1GB | ✅ |
| 专业版 | ¥299/年 | 5000 | 100 | 10GB | ✅ |
| 企业版 | ¥999/年 | 无限 | 无限 | 100GB | ✅ |

**配置位置：** `backend/app/core/plans.py`

### 6.4 原始资料管理

**功能：**
- 记录族谱的纸质/数字来源
- 关联人物与资料记录
- 可靠性评级（高/中/低）
- 验证状态追踪

### 6.5 访问统计

**统计维度：**
- 页面访问量（PV）
- 独立访客数（UV）
- 独立 IP 数
- 实时在线用户

**API 端点：**
- `/analytics/dashboard` - 仪表盘数据
- `/analytics/trends` - 访问趋势
- `/analytics/top-pages` - 热门页面
- `/analytics/realtime` - 实时数据

### 6.6 数据导出

**导出格式：** Excel（.xlsx）
- 人物列表（18 字段）
- 世代列表
- 配偶关系
- 完整数据包（多工作表）

**权限：** 专业版及以上

---

## 7. 服务端口汇总

| 服务 | 端口 | 必需 |
|------|------|:----:|
| Backend API | 8000 | ✅ |
| Frontend | 3010 | ✅ |
| SQLite | 文件 | ✅ (默认) |
| PostgreSQL | 5432 | ❌ |
| Neo4j HTTP | 7474 | ❌ |
| Neo4j Bolt | 7687 | ❌ |
| Redis | 6379 | ❌ |
| Meilisearch | 7700 | ❌ |

---

## 8. 常见问题

### Q: SQLite 支持多租户吗？

**是的！** 每个租户使用独立的 SQLite 文件：
- 系统数据库: `genealogy.db`
- 租户数据库: `tenants/{tenant_slug}.db`

### Q: SQLite 有什么限制？

SQLite 适合本地开发和小型部署：
- ✅ 零配置，开箱即用
- ✅ 单文件，易于备份和迁移
- ⚠️ 不适合高并发场景（写入并发有限）
- ⚠️ 不支持跨数据库 JOIN

生产环境推荐使用 PostgreSQL。

### Q: 如何从 SQLite 迁移到 PostgreSQL？

```bash
# 1. 导出数据
sqlite3 genealogy.db .dump > dump.sql

# 2. 转换 SQL（需调整语法）
# 3. 导入 PostgreSQL
psql -U postgres -d genealogy -f dump.sql
```

### Q: 后端启动报错？

```bash
# 确保在虚拟环境中
cd backend
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 重新安装依赖
pip install -e ".[dev]"

# 检查 .env 配置
cat .env
```

---

## 9. 最小开发配置总结

```
必需：
  ✅ Python 3.11+
  ✅ Node.js 18+
  ✅ SQLite（内置，无需安装）

可选：
  ❌ PostgreSQL（生产环境）
  ❌ Neo4j（图查询）
  ❌ Redis（缓存）
  ❌ Meilisearch（搜索）
```

**现在，只需要安装 Python 和 Node.js 就可以开始开发了！** 🚀
