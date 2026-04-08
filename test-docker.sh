#!/bin/bash
# 🚀 Local Deployment Test Script for Linux/Mac

echo ""
echo "🐳 OpenEnv Docker Deployment Test"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found! Install Docker from https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker is installed"
echo ""

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t openenv:latest .

if [ $? -ne 0 ]; then
    echo "❌ Docker build failed!"
    exit 1
fi

echo "✅ Docker image built successfully"
echo ""

# Start services
echo "🚀 Starting services with Docker Compose..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Docker Compose failed!"
    exit 1
fi

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access your application:"
echo "   - Dashboard:  http://localhost:3000"
echo "   - API:        http://localhost:8000"
echo "   - Health:     http://localhost:8000/health"
echo ""
echo "🛑 To stop services: docker-compose down"
echo "📋 To view logs:     docker-compose logs -f"
echo ""
