#!/bin/bash
# 刘氏乾正公族谱网站启动脚本

echo "=================================="
echo "  刘氏乾正公族谱网站"
echo "=================================="
echo ""

# 检查 Django 是否安装
if ! python3 -c "import django" 2>/dev/null; then
    echo "正在安装 Django..."
    pip3 install django
fi

# 检查数据库是否存在
if [ ! -f "db.sqlite3" ]; then
    echo "初始化数据库..."
    python3 manage.py migrate
    
    echo "导入族谱数据..."
    python3 import_data.py
    
    echo "创建管理员账号..."
    python3 manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123')"
fi

echo ""
echo "启动服务器..."
echo "访问地址: http://127.0.0.1:8000/"
echo "管理后台: http://127.0.0.1:8000/admin/"
echo "管理员账号: admin / admin123"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "=================================="

python3 manage.py runserver 0.0.0.0:8000
