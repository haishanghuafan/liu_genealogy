#!/bin/bash

# Deploy script for Genealogy SaaS
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_NAME="genealogy-saas"

echo "🚀 Deploying $PROJECT_NAME to $ENVIRONMENT..."

# Check if .env exists
if [ ! -f ".env.$ENVIRONMENT" ]; then
    echo "❌ Error: .env.$ENVIRONMENT not found"
    exit 1
fi

# Load environment variables
export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)

# Pull latest code
echo "📦 Pulling latest code..."
git pull origin main

# Build and deploy
echo "🔨 Building containers..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo "🚢 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check health
echo "🏥 Checking service health..."
curl -f http://localhost:8010/health || {
    echo "❌ API health check failed"
    docker-compose -f docker-compose.prod.yml logs api
    exit 1
}

# Run database migrations
echo "📊 Running database migrations..."
docker-compose -f docker-compose.prod.yml exec api alembic upgrade head

# Clear cache
echo "🧹 Clearing cache..."
docker-compose -f docker-compose.prod.yml exec redis redis-cli FLUSHALL

echo "✅ Deployment complete!"
echo ""
echo "📊 Services:"
echo "   API:      https://api.yourdomain.com"
echo "   Web:      https://yourdomain.com"
echo "   Neo4j:    http://localhost:7474"
echo "   MinIO:    http://localhost:9001"
echo ""
echo "📋 Useful commands:"
echo "   View logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.prod.yml down"
echo "   Restart API:   docker-compose -f docker-compose.prod.yml restart api"