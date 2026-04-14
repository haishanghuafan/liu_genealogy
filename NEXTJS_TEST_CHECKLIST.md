# Next.js 版本测试清单

## 核心功能测试

### 1. 认证系统 ✓
- [x] 用户注册
- [x] 用户登录
- [x] 密码修改
- [x] Token 刷新
- [x] 登录状态保持

### 2. 人物管理 ✓
- [x] 人物列表查看
- [x] 人物详情查看
- [x] 人物创建
- [x] 人物编辑
- [x] 人物删除
- [x] 人物搜索

### 3. 家族关系 ✓
- [x] 父子关系显示
- [x] 配偶关系显示
- [x] 家族树展示
- [x] 关系计算

### 4. 支系管理 ✓
- [x] 支系列表
- [x] 支系详情
- [x] 支系创建
- [x] 支系编辑
- [x] 支系统计

### 5. 世代管理 ✓
- [x] 世代列表
- [x] 世代创建
- [x] 世代编辑
- [x] 世代统计

### 6. 多租户支持 ✓
- [x] 租户隔离
- [x] 租户切换
- [x] 数据隔离

## 页面清单

### 公共页面
- [x] 首页 (/)
- [x] 登录页 (/login)
- [x] 注册页 (/register)
- [x] 密码修改页 (/change-password)

### 租户页面 (需要登录)
- [x] 工作台 (/t/[tenant])
- [x] 人物列表 (/t/[tenant]/persons)
- [x] 人物详情 (/t/[tenant]/persons/[id])
- [x] 人物编辑 (/t/[tenant]/admin/persons/[id]/edit)
- [x] 家族树 (/t/[tenant]/family-tree)
- [x] 支系列表 (/t/[tenant]/branches)
- [x] 世代列表 (/t/[tenant]/generations)

## API 端点清单

### 认证相关
- [x] POST /api/v1/auth/register
- [x] POST /api/v1/auth/login
- [x] POST /api/v1/auth/refresh
- [x] POST /api/v1/auth/change-password

### 租户相关
- [x] GET /api/v1/tenants
- [x] POST /api/v1/tenants
- [x] GET /api/v1/tenants/{slug}

### 人物相关
- [x] GET /api/v1/t/{tenant}/persons
- [x] GET /api/v1/t/{tenant}/persons/{id}
- [x] POST /api/v1/t/{tenant}/persons
- [x] PUT /api/v1/t/{tenant}/persons/{id}
- [x] DELETE /api/v1/t/{tenant}/persons/{id}

### 家族树相关
- [x] GET /api/v1/t/{tenant}/family-tree/root
- [x] GET /api/v1/t/{tenant}/family-tree/descendants/{id}
- [x] GET /api/v1/t/{tenant}/family-tree/ancestors/{id}

### 支系相关
- [x] GET /api/v1/t/{tenant}/branches
- [x] GET /api/v1/t/{tenant}/branches/{id}
- [x] POST /api/v1/t/{tenant}/branches
- [x] PUT /api/v1/t/{tenant}/branches/{id}
- [x] DELETE /api/v1/t/{tenant}/branches/{id}

### 世代相关
- [x] GET /api/v1/t/{tenant}/generations
- [x] GET /api/v1/t/{tenant}/generations/{id}
- [x] POST /api/v1/t/{tenant}/generations
- [x] PUT /api/v1/t/{tenant}/generations/{id}
- [x] DELETE /api/v1/t/{tenant}/generations/{id}

### 配偶关系相关
- [x] GET /api/v1/t/{tenant}/spouses/person/{person_id}
- [x] POST /api/v1/t/{tenant}/spouses
- [x] PUT /api/v1/t/{tenant}/spouses/{relation_id}
- [x] DELETE /api/v1/t/{tenant}/spouses/{relation_id}

## 待实现功能

### 高优先级
- [ ] Excel 数据导入
- [ ] 批量操作
- [ ] 数据导出

### 中优先级
- [ ] 文件上传（头像、图片）
- [ ] 访问统计
- [ ] 高级搜索

### 低优先级
- [ ] 数据可视化报表
- [ ] 移动端优化
- [ ] PWA 支持

## 快速启动

```bash
# 使用启动脚本
./start-nextjs.sh

# 或手动启动
# 后端
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 前端
cd frontend
npm run dev
```

## 访问地址

- 前端：http://localhost:3000
- 后端 API: http://localhost:8000
- API 文档：http://localhost:8000/api/v1/docs

## 测试账号

首次启动需要注册账号：
1. 访问 http://localhost:3000/register
2. 输入邮箱、密码、昵称
3. 注册后自动登录

## 已知问题

无严重问题

## 下一步

1. 完成剩余功能开发
2. 性能优化
3. 安全加固
4. 文档完善
5. 删除 Django 旧版本
