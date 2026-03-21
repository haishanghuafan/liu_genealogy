# liu_genealogy: 刘氏乾正公族谱网站

## 技术栈
- 后端: Django 5.2 LTS, Python 3.12+, SQLite3（生产可迁移 PostgreSQL）
- 前端: Django Templates + Bootstrap 5 + 原生 JS + jQuery
- 部署: Docker + Nginx 1.28 (stable) + gunicorn
- 工具: Pillow（图片处理）, pandas + openpyxl（数据导入）, python-dotenv

===============================================================================
# 一、全局规则

1. 这是传统 Django 全栈项目，前后端不分离，使用 Django 模板渲染
2. 所有页面必须响应式，适配手机和 PC
3. 禁止硬编码敏感信息，配置通过 .env 文件注入
4. 所有用户上传文件必须校验类型和大小（图片 ≤5MB，视频 ≤100MB）
5. 所有涉及人物数据的操作必须登录后才能修改，只读页面可匿名访问
6. 语言设置：zh-hans，时区：Asia/Shanghai
7. 静态文件生产环境通过 collectstatic 收集，由 Nginx 直接服务

===============================================================================
# 二、后端规则（Django）

## 架构规范
- 视图层：使用 Class-Based Views（CBV）或函数视图，业务简单时优先函数视图
- 禁止在视图中写复杂查询，抽取到独立函数或 Model 方法
- URL 命名必须使用 namespace：genealogy:person_detail

## 数据模型规范
- 主键使用 Django 默认 BigAutoField（族谱数据无需 UUID）
- 所有 Model 必须定义 `__str__` 和 `verbose_name`
- 人物关系（父子、配偶）通过 ForeignKey 和 ManyToManyField 建模，禁止用字符串存储关系
- 配偶关系通过 SpouseRelation 中间表管理，支持关系类型（正配/妾室/继配等）
- 文件上传必须使用 validators 校验格式和大小

## 族谱核心模型
- Generation（世代）：世代数 + 是否配偶世代，unique_together 约束
- Person（人物）：姓名、字号、生卒、父母、配偶、支系、头像
- Branch（支系）：支系名称、开基祖、分布地区
- SpouseRelation（配偶关系）：丈夫、妻子、关系类型、排序
- GenealogyRecord（族谱记录）：原始资料、来源图片、关联人物
- PageView / DailyVisitStats：访问统计

## 查询优化
- 人物列表必须使用 select_related('generation', 'father', 'branch')
- 人物详情必须 prefetch_related('spouses', 'images', 'videos', 'records')
- 禁止在模板中触发额外查询（N+1 问题）
- 访问统计写入使用 update_or_create，禁止先查后写

## 权限规范
- 只读页面（族谱浏览、人物详情）：匿名可访问
- 数据修改（新增/编辑/删除人物）：必须 @login_required
- 管理后台：仅 staff 用户可访问
- 文件上传接口：必须校验登录状态和文件合法性

## 数据导入
- Excel 导入使用 pandas + openpyxl，导入前必须校验数据完整性
- 导入失败必须回滚（使用 transaction.atomic）
- 导入结果必须返回成功/失败明细

===============================================================================
# 三、前端规则（Django Templates）

1. 所有页面继承 base.html，禁止重复引入 CSS/JS
2. 使用 Bootstrap 5 栅格系统，禁止自定义复杂布局
3. 图片使用懒加载（loading="lazy"），头像使用默认占位图
4. 族谱树形展示使用 SVG 或 Canvas，禁止用 table 嵌套模拟树形
5. 表单提交必须有 CSRF token（{% csrf_token %}）
6. Ajax 请求统一使用 fetch API，禁止 jQuery.ajax（保持代码统一）
7. 所有用户输入在前端做基础校验，后端做完整校验

===============================================================================
# 四、命名与代码风格

- Python：snake_case，类名 PascalCase
- 模板文件：{app}/{功能}.html，如 genealogy/person_detail.html
- URL name：{动词}_{名词}，如 person_detail、branch_list
- 静态文件：{app}/css/、{app}/js/、{app}/images/ 分目录存放

===============================================================================
# 五、AI 代码生成要求

1. 生成的视图必须包含权限检查
2. 生成的模板必须继承 base.html，包含响应式布局
3. 涉及文件上传必须包含类型和大小校验
4. 数据库操作涉及多步骤必须使用 transaction.atomic
5. 生成的查询必须避免 N+1，主动添加 select_related/prefetch_related

===============================================================================
# 六、优化工作规则（成型项目迭代优化）

## 基本原则
1. 优化前必须理解现有实现，禁止在未读懂代码的情况下重写
2. 每次优化范围最小化，一次只改一个模块或一个问题
3. 禁止在优化过程中顺手重构无关代码（范围蔓延）
4. 族谱数据具有历史价值，任何涉及数据删除的操作必须二次确认

## 改动前检查
- 确认改动影响范围：哪些视图、哪些模板、哪些关联模型
- 数据库变更必须评估对存量族谱数据的影响，提供迁移方案
- 涉及人物关系（父子/配偶）的改动必须梳理所有关联查询

## 代码改动规范
- 修改现有视图/函数前，先理解其所有调用方和模板引用
- 重命名 URL name 必须全局搜索所有 reverse() 和 {% url %} 引用并同步更新
- 删除代码前确认无其他模板或视图依赖，用全局搜索确认
- 性能优化必须先确认 N+1 问题的具体位置（Django Debug Toolbar 或日志）

## 模板改动规范
- 修改 base.html 前评估所有继承页面的影响
- 新增模板标签/过滤器必须在 templatetags/ 中注册，禁止在模板中写复杂逻辑
- 静态文件改动后需重新 collectstatic

## 数据库变更规范
- 禁止直接修改已有字段类型
- 新增字段必须 null=True 或有 default
- 删除字段分两步：先停止写入 → 确认无数据依赖 → 再删除
- 每次 migration 只做一件事

## 验证规范
- 改动后必须手动验证族谱核心功能：人物浏览、关系展示、图片上传
- 涉及数据库变更必须先在备份数据上验证
- 性能优化必须有前后对比（页面加载时间、SQL 查询次数）
