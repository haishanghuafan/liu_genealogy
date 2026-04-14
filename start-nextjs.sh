#!/bin/bash
# Next.js 版本快速启动和测试脚本

set -e

echo "======================================"
echo "  族谱云 Next.js 版本 - 启动脚本"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[1/4] 检查后端依赖...${NC}"
if [ ! -d "backend/venv" ]; then
    echo -e "${RED}虚拟环境不存在，请先运行：cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 后端虚拟环境已找到${NC}"

echo -e "${YELLOW}[2/4] 检查前端依赖...${NC}"
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${RED}node_modules 不存在，请先运行：cd frontend && npm install${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 前端依赖已安装${NC}"

echo ""
echo -e "${YELLOW}[3/4] 启动后端服务...${NC}"
cd backend
source venv/bin/activate
export DATABASE_URL="sqlite+aiosqlite:///./genealogy.db"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo -e "${GREEN}  访问地址：http://localhost:8000${NC}"
echo -e "${GREEN}  API 文档：http://localhost:8000/api/v1/docs${NC}"

sleep 3

echo ""
echo -e "${YELLOW}[4/4] 启动前端服务...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
echo -e "${GREEN}  访问地址：http://localhost:3000${NC}"

echo ""
echo "======================================"
echo -e "${GREEN}✓ 启动完成！${NC}"
echo "======================================"
echo ""
echo "服务访问地址:"
echo "  - 前端：http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档：http://localhost:8000/api/v1/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo ''; echo '服务已停止'; exit 0" INT

# 保持脚本运行
wait
