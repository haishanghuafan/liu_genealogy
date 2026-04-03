# Genealogy SaaS - Windows 环境安装脚本

Write-Host "======================================" -ForegroundColor Green
Write-Host " 族谱云 - 环境安装" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

$ErrorActionPreference = "Stop"

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 检查 Python
Write-Host "[1/5] 检查 Python..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "  [!!] Python 未安装，请先安装 Python 3.11+" -ForegroundColor Red
    Write-Host "      下载地址: https://www.python.org/downloads/" -ForegroundColor DarkGray
    exit 1
}
$pythonVersion = python --version
Write-Host "  [OK] $pythonVersion" -ForegroundColor Green

# 检查 Node.js
Write-Host "[2/5] 检查 Node.js..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "  [!!] Node.js 未安装，请先安装 Node.js 18+" -ForegroundColor Red
    Write-Host "      下载地址: https://nodejs.org/" -ForegroundColor DarkGray
    exit 1
}
$nodeVersion = node --version
Write-Host "  [OK] Node.js $nodeVersion" -ForegroundColor Green

# 安装后端依赖
Write-Host "[3/5] 安装后端依赖..." -ForegroundColor Yellow
$BackendDir = Join-Path $ScriptDir "backend"
Set-Location $BackendDir

if (-not (Test-Path "venv")) {
    Write-Host "  创建虚拟环境..." -ForegroundColor DarkGray
    python -m venv venv
}

Write-Host "  激活虚拟环境并安装依赖..." -ForegroundColor DarkGray
.\venv\Scripts\Activate.ps1
pip install -e ".[dev]" --quiet

if (Test-Path ".env.example") {
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "  [OK] 已创建 .env 配置文件，请检查配置" -ForegroundColor Green
    } else {
        Write-Host "  [OK] .env 已存在" -ForegroundColor Green
    }
}

Write-Host "  [OK] 后端依赖安装完成" -ForegroundColor Green

# 安装前端依赖
Write-Host "[4/5] 安装前端依赖..." -ForegroundColor Yellow
$FrontendDir = Join-Path $ScriptDir "frontend"
Set-Location $FrontendDir

npm install --silent

if (-not (Test-Path ".env.local")) {
    "@NEXT_PUBLIC_API_URL=http://localhost:8010/api/v1" | Out-File -FilePath ".env.local" -Encoding utf8
    Write-Host "  [OK] 已创建 .env.local 配置文件" -ForegroundColor Green
}

Write-Host "  [OK] 前端依赖安装完成" -ForegroundColor Green

# 完成
Write-Host ""
Write-Host "[5/5] 安装完成！" -ForegroundColor Green
Write-Host ""
Write-Host "下一步:" -ForegroundColor Cyan
Write-Host "  1. 确保已安装 PostgreSQL 数据库" -ForegroundColor White
Write-Host "  2. 修改 backend\.env 中的数据库连接信息" -ForegroundColor White
Write-Host "  3. 运行数据库迁移:" -ForegroundColor White
Write-Host "     cd backend" -ForegroundColor DarkGray
Write-Host "     .\venv\Scripts\activate" -ForegroundColor DarkGray
Write-Host "     alembic upgrade head" -ForegroundColor DarkGray
Write-Host "  4. 运行 start-dev.ps1 启动开发服务器" -ForegroundColor White
Write-Host ""
Write-Host "详细文档: docs\LOCAL_DEVELOPMENT.md" -ForegroundColor DarkGray