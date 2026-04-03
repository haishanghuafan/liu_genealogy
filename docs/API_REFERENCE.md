# 多租户族谱 SaaS 系统 - 完整功能清单

> 最后更新：2026-04-02

## 🎯 项目概述

现代化的多租族群谱管理平台，支持：
- 多家族独立管理（租户隔离）
- 族谱树可视化
- 成员协作编辑
- 订阅套餐商业化
- 完整的数据导出和原始资料管理

---

## 📦 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy 2.0 |
| 前端 | Next.js 15 + Tailwind CSS |
| 数据库 | SQLite（开发）/ PostgreSQL（生产） |
| 缓存 | Redis（可选） |
| 图数据库 | Neo4j（可选，高级图查询） |
| 搜索 | Meilisearch（可选，全文搜索） |

---

## 🗂️ 项目结构

```
liu_genealogy/
├── backend/                    # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/             # API 端点
│   │   │   └── endpoints/
│   │   │       ├── auth.py          # 认证
│   │   │       ├── tenants.py       # 租户管理
│   │   │       ├── persons.py       # 人物 CRUD + 批量导入
│   │   │       ├── family_tree.py   # 族谱树
│   │   │       ├── subscriptions.py # 订阅管理
│   │   │       ├── members.py       # 成员管理
│   │   │       ├── settings.py      # 家族设置
│   │   │       ├── files.py         # 文件上传
│   │   │       ├── search.py        # 高级搜索
│   │   │       ├── analytics.py     # 访问统计
│   │   │       ├── records.py       # 原始资料
│   │   │       └── export.py         # 数据导出
│   │   ├── models/
│   │   │   ├── system.py       # 系统级模型
│   │   │   ├── tenant.py       # 租户级模型
│   │   │   ├── records.py      # 原始资料模型
│   │   │   └── analytics.py    # 统计模型
│   │   ├── services/
│   │   │   ├── quota_service.py     # 配额服务
│   │   │   ├── visit_tracker.py     # 访问跟踪
│   │   │   └── export_service.py    # 导出服务
│   │   └── core/
│   │       ├── plans.py        # 套餐配置
│   │       ├── services.py     # 可选服务
│   │       └── database.py     # 数据库管理
│   └── pyproject.toml
│
├── frontend/                   # Next.js 前端
│   ├── app/
│   │   ├── page.tsx               # 首页
│   │   ├── login/                 # 登录
│   │   ├── register/              # 注册
│   │   ├── dashboard/             # 用户仪表盘
│   │   ├── tenants/               # 家族列表
│   │   ├── admin/tenants/         # 系统管理后台
│   │   └── t/[tenant]/
│   │       ├── page.tsx           # 租户主页
│   │       ├── family-tree/       # 族谱树
│   │       ├── admin/persons/      # 人物管理后台
│   │       ├── subscription/      # 订阅管理
│   │       ├── members/           # 成员管理
│   │       ├── settings/          # 家族设置
│   │       ├── files/             # 文件管理
│   │       ├── analytics/         # 访问统计
│   │       ├── records/           # 原始资料
│   │       └── export/            # 数据导出
│   └── components/
│       └── admin/
│           ├── PersonsList.tsx     # 人物列表（分页表单）
│           └── BatchImport.tsx     # 批量导入组件
│
└── docs/
    ├── LOCAL_DEVELOPMENT.md    # 本地开发指南
    └── API_REFERENCE.md       # API 参考文档（本文件）
```

---

## 🔌 API 端点总览（62 个）

### 系统级（7 个）

```
POST   /api/v1/auth/register       用户注册
POST   /api/v1/auth/login          用户登录
POST   /api/v1/auth/refresh        刷新 Token
GET    /api/v1/auth/me             当前用户信息
GET    /api/v1/subscription/plans   套餐列表（公开）
GET    /api/v1/tenants             租户列表
GET    /api/v1/tenants/{slug}      租户详情
```

### 租户级（55 个）

#### 人物管理（11 个）
```
GET    /t/{slug}/persons                    人物列表
POST   /t/{slug}/persons                    创建人物
POST   /t/{slug}/persons/batch-import       批量导入（CSV）
GET    /t/{slug}/persons/generations        世代列表
GET    /t/{slug}/persons/branches           支系列表
GET    /t/{slug}/persons/{id}               人物详情
PUT    /t/{slug}/persons/{id}               更新人物
DELETE /t/{slug}/persons/{id}               删除人物
GET    /t/{slug}/persons/{id}/spouses       配偶列表
POST   /t/{slug}/persons/{id}/spouses       添加配偶
DELETE /t/{slug}/persons/{id}/spouses/{sid} 删除配偶
```

#### 族谱树（4 个）
```
GET    /t/{slug}/family-tree                树数据
GET    /t/{slug}/family-tree/ancestors/{id} 祖先链
GET    /t/{slug}/family-tree/descendants/{id} 后代链
GET    /t/{slug}/family-tree/statistics     统计数据
```

#### 订阅管理（5 个）
```
GET    /t/{slug}/subscription/current       当前订阅状态
GET    /t/{slug}/subscription/quotas        配额使用情况
POST   /t/{slug}/subscription/upgrade       升级套餐
POST   /t/{slug}/subscription/cancel        取消订阅
POST   /t/{slug}/subscription/create-free   激活免费版
```

#### 成员管理（5 个）
```
GET    /t/{slug}/members                   成员列表
POST   /t/{slug}/members/invite            邀请成员
GET    /t/{slug}/members/me                我的成员信息
PUT    /t/{slug}/members/{id}/role          修改角色
DELETE /t/{slug}/members/{id}              移除成员
```

#### 家族设置（3 个）
```
GET    /t/{slug}/settings                  通用设置
PUT    /t/{slug}/settings                  更新设置
GET    /t/{slug}/settings/privacy          隐私设置
PUT    /t/{slug}/settings/privacy          更新隐私设置
GET    /t/{slug}/settings/display         显示设置
PUT    /t/{slug}/settings/display         更新显示设置
```

#### 文件管理（4 个）
```
POST   /t/{slug}/files/upload             上传文件
GET    /t/{slug}/files                     文件列表
GET    /t/{slug}/files/{filename}          下载文件
GET    /t/{slug}/files/usage               存储用量
DELETE /t/{slug}/files/{id}                删除文件
```

#### 高级搜索（3 个）
```
GET    /t/{slug}/search                    全文搜索
GET    /t/{slug}/search/advanced           高级筛选
GET    /t/{slug}/search/suggestions        搜索建议
```

#### 访问统计（4 个）
```
GET    /t/{slug}/analytics/dashboard       仪表盘数据
GET    /t/{slug}/analytics/trends          访问趋势
GET    /t/{slug}/analytics/top-pages       热门页面
GET    /t/{slug}/analytics/realtime       实时数据
```

#### 原始资料（5 个）
```
GET    /t/{slug}/records                  资料列表
POST   /t/{slug}/records                   创建记录
GET    /t/{slug}/records/{id}              资料详情
PUT    /t/{slug}/records/{id}              更新记录
DELETE /t/{slug}/records/{id}              删除记录
POST   /t/{slug}/records/{id}/persons     关联人物
DELETE /t/{slug}/records/{id}/persons/{pid} 取消关联
```

#### 数据导出（4 个）
```
GET    /t/{slug}/export/persons/excel      导出人物
GET    /t/{slug}/export/generations/excel  导出世代
GET    /t/{slug}/export/relations/excel     导出配偶关系
GET    /t/{slug}/export/full/excel         完整数据包
```

---

## 📊 数据模型

### 系统级（`public` schema）

| 模型 | 说明 |
|------|------|
| **Tenant** | 租户（家族）信息 |
| **User** | 用户账号 |
| **TenantUser** | 租户成员关系 |
| **Subscription** | 订阅记录 |
| **PageView** | 页面访问记录 |
| **DailyVisitStats** | 每日统计汇总 |
| **PageVisitStats** | 页面访问统计 |
| **TenantStats** | 租户统计快照 |

### 租户级（每个租户独立数据库）

| 模型 | 说明 |
|------|------|
| **Person** | 人物信息（28 个字段） |
| **Generation** | 世代定义 |
| **Branch** | 支系定义 |
| **SpouseRelation** | 配偶关系（9 种类型） |
| **ChangeLog** | 变更日志 |
| **PersonImage** | 人物照片 |
| **PersonVideo** | 人物视频 |
| **GenealogyRecord** | 原始资料记录 |
| **RecordPersonLink** | 资料-人物关联 |

---

## 💎 订阅套餐

| 套餐 | 价格 | 人物上限 | 成员上限 | 存储 | 高级功能 |
|------|------|----------|----------|------|----------|
| 免费版 | ¥0 | 100 | 5 | 100MB | ❌ |
| 基础版 | ¥99/年 | 500 | 20 | 1GB | ✅ |
| 专业版 | ¥299/年 | 5000 | 100 | 10GB | ✅ |
| 企业版 | ¥999/年 | 无限 | 无限 | 100GB | ✅ |

**高级功能包含：**
- 高级可视化布局
- 数据导出（Excel）
- API 访问
- 自定义域名

---

## 🎨 前端页面（17 个）

| 页面 | 路径 | 功能 |
|------|------|------|
| 首页 | `/` | 产品介绍 |
| 登录 | `/login` | 用户登录 |
| 注册 | `/register` | 用户注册 |
| 仪表盘 | `/dashboard` | 用户中心 |
| 家族列表 | `/tenants` | 浏览家族 |
| 系统后台 | `/admin/tenants` | 租户管理 |
| 租户主页 | `/t/{slug}` | 导航入口 |
| 族谱树 | `/t/{slug}/family-tree` | 可视化 |
| 人物管理后台 | `/t/{slug}/admin/persons` | CRUD |
| 订阅管理 | `/t/{slug}/subscription` | 升级/取消 |
| 成员管理 | `/t/{slug}/members` | 邀请/角色 |
| 家族设置 | `/t/{slug}/settings` | 配置 |
| 文件管理 | `/t/{slug}/files` | 上传 |
| 访问统计 | `/t/{slug}/analytics` | 数据看板 |
| 原始资料 | `/t/{slug}/records` | 资料管理 |
| 数据导出 | `/t/{slug}/export` | 下载 |

---

## 🔧 配置项

### 环境变量（`.env`）

```env
# 数据库
DATABASE_URL=sqlite+aiosqlite:///./genealogy.db

# 认证
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# 可选服务
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

REDIS_URL=redis://localhost:6379/0

MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_API_KEY=masterKey

# 套餐配置（可选覆盖默认值）
PLAN_FREE_MAX_PERSONS=100
PLAN_BASIC_PRICE_CNY=99
```

### 套餐配置文件

编辑 `backend/app/core/plans.py` 即可调整所有套餐参数：

```python
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "免费版",
        "price_cny": 0,
        "features": PlanFeatures(
            max_persons=100,
            max_members=5,
            max_storage_mb=100,
            ...
        ),
    },
    ...
}
```

---

## 📝 配偶关系类型

系统支持中国传统族谱的完整配偶关系类型：

| 代码 | 名称 | 说明 |
|------|------|------|
| `marriage` | 婚姻 | 正室 |
| `concubine` | 妾室 | 侧室 |
| `adopted` | 继配 | 继室 |
| `zhuazhui` | 招赘 | 女招男方 |
| `first` | 一房 | 大房 |
| `second` | 二房 | 二房 |
| `third` | 三房 | 三房 |
| `fourth` | 四房 | 四房 |
| `fifth` | 五房 | 五房 |

---

## 📤 导出格式

### Excel 导出

| 导出类型 | 工作表 | 字段 |
|----------|--------|------|
| 人物列表 | 人物 | 姓名、字、号、性别、世代、生卒年、出生地等 18 字段 |
| 世代列表 | 世代 | 世代数、世代名称、描述 |
| 配偶关系 | 配偶关系 | 丈夫姓名、妻子姓名、关系类型、来源信息 |
| 完整数据包 | 多工作表 | 以上全部 + 支系列表 |

### CSV 批量导入模板

```csv
name,gender,generation_id,courtesy_name,art_name,birth_year,death_year,birth_place,father_name,mother_name,biography,visibility
张三,M,1,子敬,,1950,2020,广东省梅州市,,,公开
```

---

## 🚀 快速开始

```bash
# 1. 安装后端依赖
cd backend
pip install -e ".[dev]"

# 2. 安装前端依赖
cd ../frontend
npm install

# 3. 启动服务
# 终端 1：后端
cd backend && uvicorn app.main:app --reload --port 8000

# 终端 2：前端
cd frontend && npm run dev

# 访问
open http://localhost:3010
```

---

## 📚 相关文档

- [本地开发指南](./LOCAL_DEVELOPMENT.md) - 详细的开发环境配置
- [系统架构设计](./多租户族谱%20SaaS%20系统架构设计文档.md) - 架构决策和设计
