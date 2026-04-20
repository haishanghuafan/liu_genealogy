# 族谱云 - 开发规范

## 技术栈

- **后端**: FastAPI 0.115, Python 3.11+, SQLAlchemy 2.0 (Async), Pydantic v2
- **前端**: Next.js 15, React 18, TypeScript 5, Tailwind CSS, shadcn/ui, TanStack Query
- **数据库**: SQLite3 (开发), PostgreSQL 16 (生产)
- **认证**: JWT (PyJWT)
- **部署**: Docker, Nginx, Gunicorn

---

## 一、项目架构

### 1.1 前后端分离架构

```
浏览器 <-> Next.js (前端) <-> FastAPI (后端) <-> 数据库
```

- Next.js 15 作为前端服务，监听 3000 端口
- FastAPI 作为后端 API，监听 8000 端口
- API 路径前缀: `/api/v1`
- 前端通过 `NEXT_PUBLIC_API_URL` 配置后端地址

### 1.2 多租户架构

- 租户通过 URL 路径区分: `/t/{tenant_slug}/...`
- 租户数据通过 `tenant_id` 外键隔离
- 租户中间件提取 URL 中的 tenant_slug 并注入到请求上下文

---

## 二、后端规范 (FastAPI)

### 2.1 API 端点结构

```
backend/app/api/v1/endpoints/
├── auth.py           # POST /auth/login, /auth/register
├── persons.py        # CRUD /persons
├── families.py       # 家庭关系
├── branches.py       # 支系管理
├── generations.py    # 世代管理
├── family_tree.py    # 族谱树
├── search.py         # 搜索
├── import_data.py    # Excel 导入
├── export.py         # Excel 导出
├── files.py          # 文件上传
├── tenants.py        # 租户管理
├── subscriptions.py  # 订阅管理
└── analytics.py      # 统计分析
```

### 2.2 API 响应格式

```python
# 成功响应
{"data": {...}, "message": "success"}

# 错误响应
{"detail": "错误信息"}
```

### 2.3 权限规范

| 端点类型 | 权限要求 |
|---------|---------|
| 只读 (浏览族谱) | 匿名可访问 |
| 用户操作 (注册/登录) | 公开 |
| 数据修改 (增删改) | 需要 JWT token |
| 管理功能 | 需要 admin 角色 |

### 2.4 数据库查询规范

- 列表查询使用分页: `skip`, `limit`
- 使用 `select_related` 减少关联查询
- 敏感操作使用 `transaction.atomic`

---

## 三、前端规范 (Next.js)

### 3.1 路由结构

```
frontend/app/
├── login/page.tsx              # 登录页
├── register/page.tsx           # 注册页
├── [tenant]/                   # 租户页面
│   ├── persons/[id]/page.tsx   # 人物详情
│   └── admin/                  # 管理后台
├── t/[tenant]/                 # 租户管理
│   ├── persons/page.tsx        # 人物列表
│   ├── family-tree/page.tsx    # 族谱树
│   ├── branches/page.tsx       # 支系列表
│   ├── generations/page.tsx    # 世代列表
│   ├── import/page.tsx         # 数据导入
│   ├── export/page.tsx         # 数据导出
│   └── analytics/page.tsx      # 统计分析
└── dashboard/page.tsx          # 租户选择页
```

### 3.2 组件结构

```
components/
├── ui/                    # shadcn/ui 基础组件
│   ├── button.tsx
│   ├── card.tsx
│   ├── dialog.tsx
│   ├── input.tsx
│   ├── select.tsx
│   ├── table.tsx
│   └── ...
├── family-tree/           # 族谱树组件
│   ├── FamilyTreeCanvas.tsx
│   └── FamilyTreePage.tsx
└── admin/                 # 管理组件
    ├── AdminDashboard.tsx
    └── ...
```

### 3.3 状态管理

- **服务端状态**: TanStack Query (React Query)
- **客户端状态**: React useState/useReducer
- **全局状态**: Zustand (如需要)

### 3.4 API 调用

使用 `lib/api.ts` 中的 `ApiClient`:

```typescript
import { api } from "@/lib/api"

// GET 请求
const data = await api.get<Person[]>('/persons', { tenant: 'xxx' })

// POST 请求
const result = await api.post('/persons', { name: '张三', gender: 'M' })
```

### 3.5 样式规范

- 使用 Tailwind CSS
- 颜色变量定义在 `tailwind.config.ts`
- 组件样式优先使用 shadcn/ui

---

## 四、代码风格

### 4.1 Python (后端)

- 遵循 PEP 8
- 使用类型注解
- 异步函数使用 `async def`
- 导入排序: 标准库 -> 第三方库 -> 本地模块

```python
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.tenant import Person

router = APIRouter()

@router.get("/persons", response_model=List[Person])
async def list_persons(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    ...
```

### 4.2 TypeScript (前端)

- 使用 TypeScript 5
- 接口命名: PascalCase
- 类型命名: PascalCase
- 变量/函数命名: camelCase

```typescript
interface Person {
  id: string
  name: string
  gender: 'M' | 'F'
  generation_number?: number
}

async function fetchPersons(tenant: string): Promise<Person[]> {
  return api.get<Person[]>(`/t/${tenant}/persons`)
}
```

---

## 五、文件上传规范

### 5.1 限制

| 类型 | 大小限制 | 格式 |
|------|---------|------|
| 头像图片 | 5MB | JPG, PNG, GIF, WebP |
| 族谱图片 | 10MB | JPG, PNG, PDF |
| 视频 | 100MB | MP4, AVI, MOV |

### 5.2 上传流程

1. 前端校验文件类型和大小
2. FormData 提交到 `/files/upload`
3. 后端验证并存储到 `media/` 目录
4. 返回文件 URL

---

## 六、安全规范

1. **密码存储**: 使用 bcrypt 加密
2. **JWT**: HS256 算法，设置过期时间
3. **CORS**: 仅允许配置的域名
4. **输入验证**: 使用 Pydantic 模型验证
5. **SQL注入**: 使用 SQLAlchemy ORM
6. **XSS**: React 默认转义

---

## 七、命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| API 路径 | kebab-case | `/family-tree` |
| 文件名 | kebab-case | `family-tree-page.tsx` |
| React 组件 | PascalCase | `FamilyTreePage` |
| 函数 | camelCase | `fetchPersons` |
| Python 函数 | snake_case | `get_person_by_id` |
| 数据库表 | snake_case | `family_members` |
| API 响应字段 | snake_case | `generation_number` |

---

## 八、AI 代码生成要求

### 8.1 后端 API

1. 必须包含参数验证 (Pydantic model)
2. 必须处理异常情况
3. 必须返回标准响应格式
4. 必须添加权限检查装饰器

### 8.2 前端页面

1. 使用 `use client` 指令 (客户端组件)
2. 使用 TanStack Query 进行数据获取
3. 必须处理 loading 和 error 状态
4. 必须包含响应式布局
5. 必须使用 `cn()` 合并类名

### 8.3 组件

1. 遵循 shadcn/ui 组件模式
2. 使用 `forwardRef` 处理 ref
3. 使用 `class-variance-authority` 处理样式变体

---

## 九、优化工作规则

### 9.1 基本原则

1. 优化前必须理解现有实现
2. 每次优化范围最小化
3. 禁止在优化中顺手重构无关代码
4. 族谱数据有历史价值，删除操作需二次确认

### 9.2 改动前检查

- 确认改动影响范围
- 数据库变更评估对存量数据的影响
- 涉及人物关系的改动必须梳理关联查询

### 9.3 验证规范

- 改动后必须手动验证核心功能
- 涉及数据库变更必须先在备份数据上验证
- 性能优化必须有前后对比

---

## 十、目录结构总览

```
liu_genealogy/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # API 端点
│   │   ├── core/              # 核心配置
│   │   ├── middleware/         # 中间件
│   │   ├── models/             # 数据模型
│   │   ├── services/           # 业务服务
│   │   └── main.py            # 应用入口
│   ├── tests/                 # 测试
│   └── requirements.txt
│
├── frontend/
│   ├── app/                   # 页面路由
│   ├── components/             # 组件
│   │   ├── ui/               # shadcn/ui
│   │   ├── family-tree/      # 族谱树
│   │   └── admin/            # 管理
│   ├── lib/                   # 工具库
│   │   ├── api.ts           # API 客户端
│   │   └── utils.ts         # 工具函数
│   └── package.json
│
├── docker/                    # Docker 配置
├── docs/                      # 文档
│   └── 刘氏族谱资料/          # 原始族谱数据
├── scripts/                   # 工具脚本
├── README.md                  # 项目说明
└── AGENTS.md                  # 开发规范
```
