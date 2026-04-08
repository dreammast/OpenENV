@echo off
REM 🚀 Local Deployment Test Script
REM Build and test Docker deployment locally before pushing to cloud

echo.
echo 🐳 OpenEnv Docker Deployment Test
echo ===================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker not found! Install Docker Desktop from https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo ✅ Docker is installed
echo.

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t openenv:latest .

if errorlevel 1 (
    echo ❌ Docker build failed!
    exit /b 1
)

echo ✅ Docker image built successfully
echo.

REM Option to run with docker-compose
echo 🚀 Starting services with Docker Compose...
docker-compose up -d

if errorlevel 1 (
    echo ❌ Docker Compose failed!
    exit /b 1
)

echo.
echo ✅ Services started!
echo.
echo 📍 Access your application:
echo    - Dashboard:  http://localhost:3000
echo    - API:        http://localhost:8000
echo    - Health:     http://localhost:8000/health
echo.
echo 🛑 To stop services: docker-compose down
echo 📋 To view logs:     docker-compose logs -f
echo.
pause
