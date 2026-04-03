# 多租户族谱 SaaS 系统架构设计文档

> 版本：1.0  
> 日期：2026-04-02  
> 作者：平行（AI 编程大师）

---

## 一、系统概述

### 1.1 项目背景

将现有「刘氏乾正公族谱」单租户系统重构为**多租户 SaaS 平台**，支持：
- 多个姓氏/家族独立管理族谱数据
- 租户数据严格隔离
- 分级用户权限体系
- 游客公开访问与简单搜索

### 1.2 核心目标

| 目标 | 说明 |
|------|------|
| **多租户隔离** | 每个家族数据完全隔离，互不可见 |
| **可扩展性** | 支持未来数百家族、百万级人物数据 |
| **高性能** | 族谱树渲染、关系查询秒级响应 |
| **商业化** | 订阅制收费，支持多级套餐 |

---

## 二、技术架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                         客户端层                                  │
├─────────────────────────────────────────────────────────────────┤
│  Web (Next.js)  │  H5/小程序  │  管理后台  │  开放 API          │
└────────┬────────┴──────┬──────┴─────┬──────┴────────┬───────────┘
         │               │            │               │
         └───────────────┴────────────┴───────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API 网关层                               │
├─────────────────────────────────────────────────────────────────┤
│  Nginx / Kong / AWS API Gateway                                 │
│  - 租户识别（Subdomain / Path / Header）                         │
│  - 限流、认证、日志                                              │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         应用服务层                               │
├─────────────────────────────────────────────────────────────────┤
│  FastAPI / Django REST Framework                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ 租户服务    │ │ 用户服务    │ │ 族谱服务    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ 搜索服务    │ │ 文件服务    │ │ 订阅服务    │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         数据存储层                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │ PostgreSQL  │ │   Neo4j     │ │ Redis       │               │
│  │ (关系数据)  │ │ (图数据库)  │ │ (缓存/会话) │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
│  ┌─────────────┐ ┌─────────────┐                               │
│  │ Meilisearch │ │ MinIO/OSS   │                               │
│  │ (全文检索)  │ │ (文件存储)  │                               │
│  └─────────────┘ └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 技术栈选型

| 层级 | 技术选型 | 备选方案 | 说明 |
|------|----------|----------|------|
| **前端框架** | Next.js 15 (App Router) | Nuxt 3 / SvelteKit | React 生态，SSR/SSG 支持 |
| **UI 组件** | shadcn/ui + Tailwind CSS | Ant Design / MUI | 现代化设计，高度可定制 |
| **族谱可视化** | D3.js + react-d3-tree | GoJS / G6 | 开源、灵活、功能强大 |
| **后端框架** | FastAPI | Django REST Framework | 高性能异步、自动文档 |
| **关系数据库** | PostgreSQL 16 | MySQL 8 | 支持 Schema 隔离 |
| **图数据库** | Neo4j 5 | ArangoDB | 族谱关系的最佳选择 |
| **搜索引擎** | Meilisearch | Elasticsearch | 轻量、中文支持好 |
| **缓存** | Redis 7 | Memcached | 会话、热点数据缓存 |
| **文件存储** | MinIO / 阿里云 OSS | AWS S3 | 图片、视频、文档 |
| **消息队列** | RabbitMQ / Redis Streams | Kafka | 异步任务处理 |
| **容器化** | Docker + Docker Compose | Kubernetes | 开发与部署一致性 |

---

## 三、多租户架构设计

### 3.1 租户隔离策略

**推荐方案：PostgreSQL Schema 隔离 + Neo4j 数据库隔离**

```
PostgreSQL 结构：
├── public                    # 系统级表（租户、用户、订阅）
│   ├── tenants              # 租户表
│   ├── users                # 用户表
│   ├── tenant_users         # 用户-租户关联
│   └── subscriptions        # 订阅记录
│
├── tenant_liu_qianzheng     # 刘氏乾正公族谱
│   ├── persons              # 人物
│   ├── generations          # 世代
│   ├── branches             # 支系
│   └── ...
│
├── tenant_zhang             # 张氏族谱
│   └── ...
│
└── tenant_wang              # 王氏族谱
    └── ...

Neo4j 结构：
├── system                   # 系统数据库
├── liu_qianzheng           # 刘氏图数据
├── zhang                   # 张氏图数据
└── wang                    # 王氏图数据
```

### 3.2 租户识别方式

| 方式 | 示例 | 优点 | 缺点 |
|------|------|------|------|
| **Subdomain** | `liu.genealogy.com` | 品牌独立、SEO 友好 | 需要泛域名配置 |
| **URL Path** | `/t/liu/persons/` | 部署简单 | URL 较长 |
| **Header** | `X-Tenant-ID: liu` | API 调用方便 | 浏览器访问不便 |

**推荐：Subdomain（生产环境）+ URL Path（开发/测试）**

### 3.3 租户中间件实现

```python
# middleware/tenant.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 1. 从 Subdomain 提取租户标识
        host = request.headers.get("host", "")
        subdomain = self.extract_subdomain(host)
        
        # 2. 或从 URL Path 提取
        if not subdomain:
            subdomain = self.extract_from_path(request.url.path)
        
        # 3. 加载租户信息
        if subdomain:
            tenant = await self.get_tenant(subdomain)
            request.state.tenant = tenant
            
            # 4. 切换数据库 Schema
            await self.set_tenant_schema(tenant.schema_name)
            
            # 5. 切换 Neo4j 数据库
            await self.set_neo4j_database(tenant.neo4j_database)
        
        return await call_next(request)
```

---

## 四、用户权限体系

### 4.1 用户角色定义

```
┌─────────────────────────────────────────────────────────────────┐
│                        系统级角色                                │
├─────────────────────────────────────────────────────────────────┤
│  super_admin    超级管理员    全平台管理、创建租户               │
│  operator       运营人员      用户支持、数据分析                 │
│  support        技术支持      处理技术问题                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        租户级角色                                │
├─────────────────────────────────────────────────────────────────┤
│  tenant_admin   家族管理员    家族全权限、成员管理               │
│  editor         编辑人员      增删改族谱数据                     │
│  reviewer       审核人员      审批数据变更                       │
│  member         家族成员      查看、评论、上传素材                │
│  guest          受邀访客      有限查看权限                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        公开角色                                  │
├─────────────────────────────────────────────────────────────────┤
│  anonymous      游客          查看公开内容、简单搜索             │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 权限矩阵

| 功能 | 游客 | 访客 | 成员 | 编辑 | 审核 | 家族管理员 | 超管 |
|------|:----:|:----:|:----:|:----:|:----:|:----------:|:----:|
| 查看公开人物 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 简单搜索 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 高级搜索 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 查看私密人物 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| 添加/编辑人物 | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| 删除人物 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| 审批变更 | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| 成员管理 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| 家族设置 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| 创建新家族 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| 平台管理 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### 4.3 权限实现

```python
# permissions.py
from enum import Enum
from functools import wraps

class Permission(Enum):
    VIEW_PUBLIC = "view_public"
    VIEW_PRIVATE = "view_private"
    SEARCH_BASIC = "search_basic"
    SEARCH_ADVANCED = "search_advanced"
    CREATE_PERSON = "create_person"
    EDIT_PERSON = "edit_person"
    DELETE_PERSON = "delete_person"
    APPROVE_CHANGE = "approve_change"
    MANAGE_MEMBERS = "manage_members"
    MANAGE_TENANT = "manage_tenant"
    MANAGE_PLATFORM = "manage_platform"

ROLE_PERMISSIONS = {
    "anonymous": {Permission.VIEW_PUBLIC, Permission.SEARCH_BASIC},
    "guest": {Permission.VIEW_PUBLIC, Permission.SEARCH_BASIC, Permission.SEARCH_ADVANCED},
    "member": {Permission.VIEW_PUBLIC, Permission.SEARCH_BASIC, Permission.SEARCH_ADVANCED},
    "editor": {Permission.VIEW_PUBLIC, Permission.SEARCH_BASIC, Permission.SEARCH_ADVANCED,
               Permission.CREATE_PERSON, Permission.EDIT_PERSON},
    "reviewer": {Permission.VIEW_PUBLIC, Permission.SEARCH_BASIC, Permission.SEARCH_ADVANCED,
                 Permission.CREATE_PERSON, Permission.EDIT_PERSON, Permission.APPROVE_CHANGE},
    "tenant_admin": {Permission.VIEW_PUBLIC, Permission.VIEW_PRIVATE, Permission.SEARCH_BASIC,
                     Permission.SEARCH_ADVANCED, Permission.CREATE_PERSON, Permission.EDIT_PERSON,
                     Permission.DELETE_PERSON, Permission.APPROVE_CHANGE, Permission.MANAGE_MEMBERS,
                     Permission.MANAGE_TENANT},
    "super_admin": set(Permission),  # 所有权限
}

def require_permission(permission: Permission):
    def decorator(func):
        @wraps(func)
        async def wrapper(request, *args, **kwargs):
            user = request.state.user
            if not user:
                raise HTTPException(401, "未登录")
            
            user_permissions = ROLE_PERMISSIONS.get(user.role, set())
            if permission not in user_permissions:
                raise HTTPException(403, "权限不足")
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
```

---

## 五、数据模型设计

### 5.1 系统级模型（public schema）

```sql
-- 租户表
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,              -- 家族名称
    slug VARCHAR(50) UNIQUE NOT NULL,        -- URL 标识
    surname VARCHAR(50) NOT NULL,            -- 姓氏
    schema_name VARCHAR(50) UNIQUE NOT NULL, -- PostgreSQL Schema
    neo4j_database VARCHAR(50) NOT NULL,     -- Neo4j 数据库名
    
    -- 订阅信息
    plan VARCHAR(20) DEFAULT 'free',
    max_members INTEGER DEFAULT 100,
    max_persons INTEGER DEFAULT 500,
    max_storage_mb INTEGER DEFAULT 500,
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT TRUE,
    
    -- 元信息
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP,
    
    -- 配置
    settings JSONB DEFAULT '{}'
);

-- 用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(500),
    
    -- 系统角色
    system_role VARCHAR(20) DEFAULT 'user',  -- user, operator, super_admin
    
    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

-- 用户-租户关联
CREATE TABLE tenant_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    role VARCHAR(20) DEFAULT 'member',       -- guest, member, editor, reviewer, tenant_admin
    
    -- 关联的族谱人物
    person_id UUID,                          -- 指向租户 schema 的 person 表
    
    joined_at TIMESTAMP DEFAULT NOW(),
    invited_by UUID REFERENCES users(id),
    
    UNIQUE(user_id, tenant_id)
);

-- 订阅记录
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id),
    plan VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2),
    currency VARCHAR(10) DEFAULT 'CNY',
    
    started_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    
    status VARCHAR(20) DEFAULT 'active',     -- active, expired, cancelled
    
    payment_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5.2 租户级模型（tenant schema）

```sql
-- 人物表
CREATE TABLE persons (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 基本信息
    name VARCHAR(100) NOT NULL,
    courtesy_name VARCHAR(100),              -- 字
    art_name VARCHAR(100),                   -- 号
    alias VARCHAR(100),                      -- 别名
    generation_char VARCHAR(10),             -- 辈份字
    
    gender CHAR(1) DEFAULT 'M',              -- M/F
    is_outsider BOOLEAN DEFAULT FALSE,       -- 是否外族配偶
    
    -- 世代
    generation_id INTEGER,
    
    -- 父母（自关联）
    father_id UUID REFERENCES persons(id),
    mother_id UUID REFERENCES persons(id),
    
    -- 支系
    branch_id UUID REFERENCES branches(id),
    
    -- 生卒信息
    birth_year INTEGER,
    death_year INTEGER,
    birth_place VARCHAR(200),
    lunar_birthday VARCHAR(50),              -- 农历生日
    
    -- 墓葬
    burial_place VARCHAR(300),
    burial_fengshui VARCHAR(200),
    burial_direction VARCHAR(100),
    
    -- 生平
    biography TEXT,
    achievements TEXT,
    descendants_location TEXT,
    notes TEXT,
    
    -- 隐私控制
    visibility VARCHAR(20) DEFAULT 'public', -- public, member, private
    
    -- 排序
    sort_order INTEGER DEFAULT 0,
    
    -- 头像
    avatar VARCHAR(500),
    
    -- 元信息
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by UUID,
    
    -- 全文搜索向量
    search_vector TSVECTOR
);

-- 配偶关系
CREATE TABLE spouse_relations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    husband_id UUID REFERENCES persons(id) ON DELETE CASCADE,
    wife_id UUID REFERENCES persons(id) ON DELETE CASCADE,
    
    relation_type VARCHAR(20) DEFAULT 'marriage',
    source_info VARCHAR(200),                -- 配偶来源
    sort_order INTEGER DEFAULT 1,
    
    UNIQUE(husband_id, wife_id)
);

-- 世代
CREATE TABLE generations (
    id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    is_spouse BOOLEAN DEFAULT FALSE,
    name VARCHAR(50),
    description TEXT,
    
    UNIQUE(number, is_spouse)
);

-- 支系
CREATE TABLE branches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    founder_id UUID REFERENCES persons(id),
    description TEXT,
    location VARCHAR(200)
);

-- 人物图片
CREATE TABLE person_images (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID REFERENCES persons(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    title VARCHAR(100),
    description TEXT,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 人物视频
CREATE TABLE person_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID REFERENCES persons(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    title VARCHAR(100),
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 变更历史
CREATE TABLE change_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name VARCHAR(50) NOT NULL,
    record_id UUID NOT NULL,
    action VARCHAR(20) NOT NULL,             -- create, update, delete
    old_values JSONB,
    new_values JSONB,
    
    changed_by UUID REFERENCES tenant_users(id),
    changed_at TIMESTAMP DEFAULT NOW(),
    
    -- 审核状态
    review_status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected
    reviewed_by UUID,
    reviewed_at TIMESTAMP,
    review_notes TEXT
);
```

### 5.3 Neo4j 图模型

```cypher
// 人物节点
CREATE (p:Person {
    id: 'uuid',
    name: '姓名',
    generation: 5,
    birth_year: 1950,
    tenant_id: 'liu_qianzheng'
})

// 父子关系
CREATE (father:Person {id: 'father_uuid'})
CREATE (child:Person {id: 'child_uuid'})
CREATE (father)-[:FATHER_OF]->(child)
CREATE (child)-[:CHILD_OF]->(father)

// 配偶关系
CREATE (husband:Person {id: 'h_uuid', gender: 'M'})
CREATE (wife:Person {id: 'w_uuid', gender: 'F'})
CREATE (husband)-[:MARRIED {type: 'marriage', order: 1}]->(wife)

// 支系关系
CREATE (founder:Person {id: 'f_uuid'})
CREATE (branch:Branch {id: 'b_uuid', name: '长房'})
CREATE (founder)-[:FOUNDED]->(branch)
CREATE (member:Person)-[:BELONGS_TO]->(branch)
```

---

## 六、API 设计

### 6.1 API 路由结构

```
/api/v1/
├── /auth                      # 认证（无需租户）
│   ├── POST /register         # 注册
│   ├── POST /login            # 登录
│   ├── POST /logout           # 登出
│   ├── POST /refresh          # 刷新 Token
│   └── GET  /me               # 当前用户信息
│
├── /tenants                   # 租户管理（系统级）
│   ├── GET  /                 # 租户列表（公开）
│   ├── POST /                 # 创建租户（超管）
│   ├── GET  /{slug}           # 租户详情
│   └── PUT  /{slug}           # 更新租户（管理员）
│
├── /t/{tenant_slug}           # 租户级 API
│   ├── /persons
│   │   ├── GET  /             # 人物列表
│   │   ├── POST /             # 创建人物
│   │   ├── GET  /{id}         # 人物详情
│   │   ├── PUT  /{id}         # 更新人物
│   │   └── DELETE /{id}       # 删除人物
│   │
│   ├── /family-tree
│   │   ├── GET  /             # 族谱树数据
│   │   ├── GET  /ancestors/{id}   # 祖先链
│   │   └── GET  /descendants/{id} # 后代链
│   │
│   ├── /search
│   │   ├── GET  /             # 搜索人物
│   │   └── GET  /advanced     # 高级搜索
│   │
│   ├── /members
│   │   ├── GET  /             # 成员列表
│   │   ├── POST /invite       # 邀请成员
│   │   └── PUT  /{id}/role    # 修改角色
│   │
│   └── /settings
│       ├── GET  /             # 家族设置
│       └── PUT  /             # 更新设置
│
└── /admin                     # 系统管理（超管）
    ├── /tenants
    ├── /users
    └── /stats
```

### 6.2 API 响应格式

```json
// 成功响应
{
    "success": true,
    "data": { ... },
    "meta": {
        "total": 100,
        "page": 1,
        "page_size": 20
    }
}

// 错误响应
{
    "success": false,
    "error": {
        "code": "PERMISSION_DENIED",
        "message": "您没有权限执行此操作",
        "details": {}
    }
}
```

---

## 七、前端架构

### 7.1 项目结构

```
genealogy-saas-web/
├── app/
│   ├── (public)/                 # 公开页面
│   │   ├── page.tsx             # 首页
│   │   ├── tenants/             # 家族列表
│   │   └── [tenant]/            # 租户公开页面
│   │       ├── page.tsx         # 家族首页
│   │       ├── family-tree/     # 族谱树
│   │       ├── persons/         # 人物列表
│   │       └── person/[id]/     # 人物详情
│   │
│   ├── (auth)/                   # 认证
│   │   ├── login/
│   │   ├── register/
│   │   └── forgot-password/
│   │
│   ├── (dashboard)/              # 用户中心
│   │   ├── page.tsx             # 仪表盘
│   │   ├── my-tenants/          # 我的家族
│   │   └── settings/            # 个人设置
│   │
│   ├── (tenant-admin)/           # 家族管理
│   │   └── [tenant]/
│   │       ├── dashboard/       # 数据概览
│   │       ├── persons/         # 人物管理
│   │       ├── members/         # 成员管理
│   │       ├── changes/         # 变更审核
│   │       └── settings/        # 家族设置
│   │
│   ├── (admin)/                  # 系统管理
│   │   ├── tenants/             # 租户管理
│   │   ├── users/               # 用户管理
│   │   └── stats/               # 统计分析
│   │
│   └── api/                      # API Routes
│       └── [...]/               # BFF 层
│
├── components/
│   ├── ui/                       # 基础 UI 组件
│   ├── family-tree/              # 族谱树组件
│   ├── person/                   # 人物相关组件
│   └── shared/                   # 共享组件
│
├── lib/
│   ├── api/                      # API 客户端
│   ├── auth/                     # 认证逻辑
│   ├── tenant/                   # 租户上下文
│   └── utils/                    # 工具函数
│
├── hooks/                        # 自定义 Hooks
├── stores/                       # 状态管理
├── types/                        # TypeScript 类型
└── styles/                       # 样式文件
```

### 7.2 核心组件设计

```tsx
// components/family-tree/FamilyTreeCanvas.tsx
'use client'

import { useCallback, useEffect, useState } from 'react'
import { Tree } from 'react-d3-tree'

interface FamilyTreeProps {
  tenantSlug: string
  rootPersonId?: string
}

export function FamilyTreeCanvas({ tenantSlug, rootPersonId }: FamilyTreeProps) {
  const [treeData, setTreeData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchTreeData()
  }, [tenantSlug, rootPersonId])

  const fetchTreeData = async () => {
    const res = await fetch(`/api/v1/t/${tenantSlug}/family-tree?root=${rootPersonId || ''}`)
    const data = await res.json()
    setTreeData(data.data)
    setLoading(false)
  }

  if (loading) return <FamilyTreeSkeleton />

  return (
    <div className="w-full h-[800px]">
      <Tree
        data={treeData}
        orientation="vertical"
        pathFunc="step"
        translate={{ x: 400, y: 50 }}
        nodeSize={{ x: 200, y: 100 }}
        renderCustomNodeElement={PersonNode}
        onNodeClick={handleNodeClick}
        zoomable
        draggable
      />
    </div>
  )
}

// 自定义人物节点
function PersonNode({ nodeData }) {
  return (
    <foreignObject width={180} height={80} x={-90} y={-40}>
      <div className="bg-white rounded-lg shadow-md p-2 border hover:border-primary-500 transition">
        <div className="flex items-center gap-2">
          <Avatar src={nodeData.avatar} size="sm" />
          <div>
            <div className="font-medium text-sm">{nodeData.name}</div>
            <div className="text-xs text-gray-500">第{nodeData.generation}世</div>
          </div>
        </div>
      </div>
    </foreignObject>
  )
}
```

---

## 八、数据迁移方案

### 8.1 迁移步骤

```
Phase 1: 准备阶段
├── 1.1 部署新系统基础架构
├── 1.2 创建 tenant_liu_qianzheng 租户
└── 1.3 创建 Schema 和数据库

Phase 2: 数据导出
├── 2.1 导出 Django 数据为 JSON
├── 2.2 导出图片/视频文件
└── 2.3 导出族谱关系数据

Phase 3: 数据转换
├── 3.1 转换人物数据格式
├── 3.2 转换关系数据
├── 3.3 生成 Neo4j 导入脚本
└── 3.4 上传文件到对象存储

Phase 4: 数据导入
├── 4.1 导入 PostgreSQL
├── 4.2 导入 Neo4j
├── 4.3 建立搜索索引
└── 4.4 验证数据完整性

Phase 5: 切换上线
├── 5.1 配置域名指向
├── 5.2 迁移用户账号
└── 5.3 关闭旧系统
```

### 8.2 迁移脚本示例

```python
# scripts/migrate_data.py
import json
from pathlib import Path

def export_django_data():
    """导出 Django 数据"""
    from genealogy.models import Person, Generation, Branch, SpouseRelation
    
    data = {
        'persons': [],
        'generations': [],
        'branches': [],
        'spouse_relations': []
    }
    
    for p in Person.objects.all():
        data['persons'].append({
            'id': str(p.id),
            'name': p.name,
            'courtesy_name': p.courtesy_name,
            'gender': p.gender,
            'birth_year': p.birth_year,
            'generation_id': p.generation_id,
            'father_id': str(p.father_id) if p.father else None,
            'mother_id': str(p.mother_id) if p.mother else None,
            'branch_id': str(p.branch_id) if p.branch else None,
            # ...
        })
    
    return data

def generate_neo4j_import(persons, relations):
    """生成 Neo4j 导入 Cypher"""
    cypher = []
    
    # 创建人物节点
    for p in persons:
        cypher.append(f"""
        CREATE (p:Person {{
            id: '{p['id']}',
            name: '{p['name']}',
            generation: {p['generation_id']}
        }})
        """)
    
    # 创建关系
    for p in persons:
        if p['father_id']:
            cypher.append(f"""
            MATCH (child:Person {{id: '{p['id']}'}})
            MATCH (father:Person {{id: '{p['father_id']}'}})
            CREATE (father)-[:FATHER_OF]->(child)
            """)
    
    return '\n'.join(cypher)
```

---

## 九、部署架构

### 9.1 Docker Compose 开发环境

```yaml
# docker-compose.yml
version: '3.8'

services:
  # 前端
  web:
    build: ./frontend
    ports:
      - "3010:3010"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8010
    depends_on:
      - api

  # 后端 API
  api:
    build: ./backend
    ports:
      - "8010:8010"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/genealogy
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - neo4j
      - redis

  # PostgreSQL
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: genealogy
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - pg_data:/var/lib/postgresql/data

  # Neo4j
  neo4j:
    image: neo4j:5
    environment:
      NEO4J_AUTH: neo4j/password
    ports:
      - "7474:7474"  # HTTP
      - "7687:7687"  # Bolt
    volumes:
      - neo4j_data:/data

  # Redis
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  # Meilisearch
  meilisearch:
    image: getmeili/meilisearch:latest
    ports:
      - "7700:7700"
    volumes:
      - meili_data:/meili_data

  # MinIO (本地对象存储)
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

volumes:
  pg_data:
  neo4j_data:
  redis_data:
  meili_data:
  minio_data:
```

### 9.2 生产环境架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         CDN / WAF                               │
│                    (Cloudflare / 阿里云 CDN)                     │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      负载均衡 (SLB)                              │
│                     Nginx / Kong                                │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │ Web 1  │    │ Web 2  │    │ Web N  │
         └────┬───┘    └────┬───┘    └────┬───┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                       API 服务集群                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ API Pod 1│  │ API Pod 2│  │ API Pod 3│  │ API Pod N│        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────┬────────────────────────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌────────┐    ┌────────┐    ┌────────┐
         │Postgres│    │ Neo4j  │    │ Redis  │
         │ 主从   │    │ 集群   │    │ 集群   │
         └────────┘    └────────┘    └────────┘
```

---

## 十、商业化设计

### 10.1 订阅套餐

| 功能 | 免费版 | 基础版 | 专业版 | 企业版 |
|------|--------|--------|--------|--------|
| 价格 | ¥0 | ¥99/年 | ¥299/年 | ¥999/年 |
| 最大人物数 | 100 | 500 | 5,000 | 无限 |
| 管理员数 | 1 | 3 | 10 | 无限 |
| 存储空间 | 100MB | 1GB | 10GB | 100GB |
| 高级可视化 | ❌ | ✅ | ✅ | ✅ |
| 数据导出 | ❌ | ✅ | ✅ | ✅ |
| API 访问 | ❌ | ❌ | ✅ | ✅ |
| 自定义域名 | ❌ | ❌ | ❌ | ✅ |
| 优先支持 | 社区 | 邮件 | 优先 | 专属 |

### 10.2 收入预测（示例）

| 场景 | 套餐 | 数量 | 年收入 |
|------|------|------|--------|
| 小型家族 | 基础版 | 100 个 | ¥9,900 |
| 中型家族 | 专业版 | 50 个 | ¥14,950 |
| 大型家族 | 企业版 | 10 个 | ¥9,990 |
| **合计** | - | 160 个 | **¥34,840** |

---

## 十一、开发计划

### 11.1 阶段规划

| 阶段 | 内容 | 周期 |
|------|------|------|
| **Phase 1** | 项目骨架搭建、数据库设计、租户系统 | 1-2 周 |
| **Phase 2** | 用户认证、权限系统、人物管理 | 2 周 |
| **Phase 3** | 族谱树可视化（D3.js）、Neo4j 集成 | 2-3 周 |
| **Phase 4** | 搜索引擎、文件上传、数据迁移 | 1-2 周 |
| **Phase 5** | 前端优化、移动适配、PWA | 1 周 |
| **Phase 6** | 支付系统、订阅管理、上线 | 1 周 |

### 11.2 技术风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| Neo4j 学习曲线 | 中 | 先用 PostgreSQL 实现，后期迁移 |
| 大规模族谱树渲染性能 | 高 | 虚拟滚动、懒加载、WebGL |
| 多租户数据隔离 | 高 | 严格测试、代码审查、权限边界检查 |
| 数据迁移复杂性 | 中 | 编写迁移脚本、分批迁移、验证工具 |

---

## 十二、总结

本架构设计文档提供了一个完整的多租户族谱 SaaS 解决方案：

1. **技术先进**：Next.js + FastAPI + Neo4j + PostgreSQL
2. **架构合理**：多租户隔离、微服务化、可扩展
3. **权限清晰**：系统级、租户级、公开级三层权限
4. **商业化可行**：订阅制、多套餐、支付集成

---

**文档版本历史：**

| 版本 | 日期 | 修改内容 |
|------|------|----------|
| 1.0 | 2026-04-02 | 初始版本 |