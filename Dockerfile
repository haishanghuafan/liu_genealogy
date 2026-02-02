# 使用Python 3.12 Alpine作为基础镜像
FROM python:3.12-alpine

# 设置工作目录
WORKDIR /app

# 配置国内apk镜像源（清华源）
RUN echo "https://mirrors.tuna.tsinghua.edu.cn/alpine/latest-stable/main" > /etc/apk/repositories \
    && echo "https://mirrors.tuna.tsinghua.edu.cn/alpine/latest-stable/community" >> /etc/apk/repositories

# 安装系统依赖
RUN apk add --no-cache \
    nginx \
    curl \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev

# 复制requirements.txt文件
COPY requirements.txt .
# 配置pip使用清华源
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制nginx配置文件
COPY nginx.conf /etc/nginx/nginx.conf

# 复制启动脚本
COPY start.sh .
RUN chmod +x start.sh

# 暴露80端口
EXPOSE 80

# 启动命令
CMD ["./start.sh"]

