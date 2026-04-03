# Genealogy SaaS - Windows 开发环境启动脚本

Write-Host "======================================" -ForegroundColor Green
Write-Host " 族谱云 - 开发环境启动" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""

$ErrorActionPreference = "Continue"

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 检查服务
Write-Host "[1/4] 检查依赖服务..." -ForegroundColor Yellow

# PostgreSQL
$pg = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
if ($pg -and $pg.Status -eq "Running") {
    Write-Host "  [OK] PostgreSQL 运行中" -ForegroundColor Green
} else {
    Write-Host "  [!!] PostgreSQL 未运行，请手动启动" -ForegroundColor Red
}

# Redis
$redis = Get-Service -Name "Redis*" -ErrorAction SilentlyContinue
if ($redis -and $redis.Status -eq "Running") {
    Write-Host "  [OK] Redis 运行中" -ForegroundColor Green
} else {
    Write-Host "  [--] Redis 未安装或未运行（可选）" -ForegroundColor DarkGray
}

# Neo4j
$neo4j = Get-Service -Name "Neo4j*" -ErrorAction SilentlyContinue
if ($neo4j -and $neo4j.Status -eq "Running") {
    Write-Host "  [OK] Neo4j 运行中" -ForegroundColor Green
} else {
    Write-Host "  [--] Neo4j 未安装或未运行（可选）" -ForegroundColor DarkGray
}

Write-Host ""

# 启动后端
Write-Host "[2/4] 启动后端服务..." -ForegroundColor Yellow

$BackendDir = Join-Path $ScriptDir "backend"
$VenvActivate = Join-Path $BackendDir "venv\Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    # 启动后端（新窗口）
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$BackendDir'; .\venv\Scripts\Activate.ps1; Write-Host '后端服务运行中 - http://localhost:8010' -ForegroundColor Green; uvicorn app.main:app --reload --port 8010"
    )
    Write-Host "  [OK] 后端服务已启动 (端口 8010)" -ForegroundColor Green
} else {
    Write-Host "  [!!] 虚拟环境不存在，请先运行 setup.ps1" -ForegroundColor Red
}

Start-Sleep -Seconds 2

# 启动前端
Write-Host "[3/4] 启动前端服务..." -ForegroundColor Yellow

$FrontendDir = Join-Path $ScriptDir "frontend"

if (Test-Path (Join-Path $FrontendDir "node_modules")) {
    # 启动前端（新窗口）
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "cd '$FrontendDir'; Write-Host '前端服务运行中 - http://localhost:3010' -ForegroundColor Green; npm run dev"
    )
    Write-Host "  [OK] 前端服务已启动 (端口 3010)" -ForegroundColor Green
} else {
    Write-Host "  [!!] node_modules 不存在，请先运行 npm install" -ForegroundColor Red
}

Write-Host ""

# 显示访问地址
Write-Host "[4/4] 服务地址" -ForegroundColor Yellow
Write-Host "  前端:     http://localhost:3010" -ForegroundColor Cyan
Write-Host "  后端 API: http://localhost:8010" -ForegroundColor Cyan
Write-Host "  API 文档: http://localhost:8010/api/v1/docs" -ForegroundColor Cyan
Write-Host "  Neo4j:    http://localhost:7474" -ForegroundColor Cyan

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host " 启动完成！按任意键退出此窗口" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green

$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")