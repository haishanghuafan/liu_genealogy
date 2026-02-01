# 刘氏乾正公族谱网站

基于 Django + SQLite3 构建的现代化族谱网站，用于记录和管理广东省梅州市梅县梅西田福刘氏乾正公世系的家族传承信息。

## 功能特性

- **首页展示**：家族统计、始祖介绍、快速导航
- **世系图**：可视化展示家族传承关系
- **人物管理**：详细的人物信息（姓名、字号、生卒、墓葬等）
- **支系管理**：各支系的分布和成员
- **世代列表**：按世代浏览人物
- **搜索功能**：支持按姓名、字号、事迹搜索
- **用户系统**：注册、登录、修改密码、个人资料
- **管理后台**：完整的后台管理系统

## 技术栈

- **后端**：Django 6.0.1
- **数据库**：SQLite3
- **前端**：Bootstrap 5 + Bootstrap Icons
- **字体**：Google Fonts (Noto Serif SC, Noto Sans SC)

## 项目结构

```
liu_genealogy/
├── liu_genealogy/          # 项目配置
│   ├── __init__.py
│   ├── settings.py         # 项目设置
│   ├── urls.py             # 主路由
│   ├── wsgi.py
│   └── asgi.py
├── genealogy/              # 族谱应用
│   ├── __init__.py
│   ├── admin.py            # 后台管理配置
│   ├── apps.py
│   ├── models.py           # 数据模型
│   ├── views.py            # 视图
│   ├── urls.py             # 应用路由
│   ├── migrations/         # 数据库迁移
│   └── templates/          # HTML模板
│       └── genealogy/
├── templates/              # 基础模板
│   └── base.html
├── static/                 # 静态文件
│   ├── css/
│   ├── js/
│   └── images/
├── manage.py               # Django管理脚本
├── import_data.py          # 数据导入脚本
└── README.md               # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install django
```

### 2. 数据库迁移

```bash
python manage.py migrate
```

### 3. 导入族谱数据

```bash
python import_data.py
```

### 4. 创建超级用户

```bash
python manage.py createsuperuser
```

### 5. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 查看网站

## 管理员登录

- 地址：http://127.0.0.1:8000/admin/
- 默认账号：admin
- 默认密码：admin123

## 数据模型

### Generation（世代）
- number: 世代数
- name: 世代名称
- description: 描述

### Branch（支系）
- name: 支系名称
- founder: 开基祖
- description: 描述
- location: 分布地区

### Person（人物）
- name: 姓名
- courtesy_name: 字
- art_name: 号
- alias: 别名
- gender: 性别
- generation: 所属世代
- father/mother: 父母
- spouses: 配偶
- branch: 所属支系
- birth_year/death_year: 生卒年份
- burial_place: 葬地
- biography: 生平简介
- descendants_location: 后裔分布

## 路由说明

| 路径 | 说明 |
|------|------|
| / | 首页 |
| /tree/ | 世系图 |
| /persons/ | 人物列表 |
| /person/<id>/ | 人物详情 |
| /branches/ | 支系列表 |
| /branch/<id>/ | 支系详情 |
| /generations/ | 世代列表 |
| /search/ | 搜索 |
| /login/ | 登录 |
| /register/ | 注册 |
| /password_change/ | 修改密码 |
| /profile/ | 个人资料 |
| /admin/ | 管理后台 |

## 后续维护

### 添加新人物

1. 登录管理后台：http://127.0.0.1:8000/admin/
2. 进入 "人物" 管理
3. 点击 "添加人物"
4. 填写相关信息并保存

### 修改数据

可以直接在管理后台修改人物、支系、世代等信息。

### 备份数据库

SQLite 数据库文件位于项目根目录的 `db.sqlite3`，直接备份此文件即可。

## 自定义配置

编辑 `liu_genealogy/settings.py` 文件可修改：

- 网站语言、时区
- 静态文件路径
- 数据库配置
- 密码验证规则
- 会话设置

## 部署说明

### 生产环境配置

1. 修改 `settings.py`：
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. 收集静态文件：
   ```bash
   python manage.py collectstatic
   ```

3. 使用 Gunicorn/uWSGI + Nginx 部署

### 使用 Gunicorn

```bash
pip install gunicorn
gunicorn liu_genealogy.wsgi:application --bind 0.0.0.0:8000
```

## 数据来源

- 《广东省梅州市梅县梅西田福刘氏乾正公族谱世系》
- 《梅西田福刘氏族谱世系》（粗稿供研讨）

## 版权说明

根据田福宗亲收藏本及梅县刘氏族谱整理，供研考和寻根问祖之用。

---

**刘氏乾正公族谱网站**  
广东省梅州市梅县梅西田福  
铭记祖德 · 传承家风 · 团结互助
