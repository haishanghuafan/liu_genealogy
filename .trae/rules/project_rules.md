# 刘氏乾正公族谱项目开发规则

## 项目概述
这是一个基于Django的族谱管理系统，用于管理刘氏乾正公家族的世代关系、族谱记录和人物信息。

## 技术栈
- 后端：Django 5.2.11
- 数据库：使用Django ORM（可能连接PostgreSQL）
- 前端：HTML模板 + JavaScript
- 文件处理：Pandas, OpenPyxl, Pillow
- 部署：Docker, Gunicorn

## 代码规范

### Python/Django规范
- 遵循PEP 8编码规范
- 使用类型注解
- 所有函数和类需要文档字符串
- 使用Django内置功能，如ORM、认证系统等
- 模型字段必须包含verbose_name以支持中文界面

### 模型设计原则
- 使用models.py中已定义的验证函数（validate_file_size, validate_image_extension等）
- 正确设置Meta类中的verbose_name和ordering
- 合理使用外键关系（ForeignKey）和多对多关系（ManyToManyField）
- 定义__str__方法便于后台显示

### 数据模型关键概念
- Generation（世代）：代表族谱的代数层次
- Person（人物）：族谱中的个体成员
- SpouseRelation（夫妻关系）：连接不同世代的夫妻关系
- GenealogyRecord（族谱记录）：包含来源和相关人物

## 开发实践

### 安全性
- 输入验证：所有用户输入必须验证
- 文件上传：使用预定义的验证器限制文件类型和大小
- 权限控制：正确使用Django权限系统
- 防止SQL注入：始终使用Django ORM查询

### 性能优化
- 查询优化：使用select_related和prefetch_related减少数据库查询
- 分页：对于列表页面实现分页
- 缓存：合理使用Django缓存框架
- 静态文件：正确配置静态文件服务

### 国际化与本地化
- 支持中文界面
- 模型字段使用中文verbose_name
- 模板中使用翻译标签

## 项目结构
```
genealogy/                 # 主应用
├── models.py             # 数据模型定义
├── views.py              # 视图逻辑
├── urls.py               # URL路由
├── admin.py              # 管理后台配置
├── permissions.py        # 权限控制
├── migrations/           # 数据库迁移
├── static/genealogy/     # 静态资源
└── templates/genealogy/  # 模板文件
liu_genealogy/            # 项目配置
├── settings.py           # 项目设置
├── urls.py               # 根路由
└── ...
templates/base.html       # 基础模板
media/                    # 媒体文件存储
docs/                     # 文档资料
```

## 特殊业务规则

### 族谱数据管理
- 世代关系必须保持逻辑一致性
- 夫妻关系的处理：区分夫与妻的角色
- 外部人员标识：使用is_outsider字段标记非刘氏成员
- 配偶世代处理：is_spouse标志用于区分配偶世代

### 文件上传限制
- 图片：最大5MB，支持JPG、JPEG、PNG、GIF、WebP
- 视频：最大100MB，支持MP4、AVI、MOV、WMV、FLV
- 记录来源图片：最大10MB

### 用户权限
- 区分普通用户和管理员权限
- 敏感操作需要身份验证
- 数据修改需审核机制

## 测试要求
- 单元测试覆盖核心业务逻辑
- 模型验证测试
- 视图访问权限测试
- 文件上传安全测试

## 部署规则
- 使用Docker容器化部署
- 环境变量通过.env文件管理
- 生产环境使用Gunicorn服务器
- 静态文件由Nginx服务

## 维护建议
- 定期备份数据库
- 监控文件存储空间
- 检查数据一致性
- 更新依赖包安全补丁