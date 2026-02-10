#!/bin/sh

# 创建必要的目录
mkdir -p /app/media /app/static /app/logs

# 收集静态文件
python manage.py collectstatic --noinput

# 启动nginx服务
nginx

# 启动gunicorn服务
gunicorn liu_genealogy.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log