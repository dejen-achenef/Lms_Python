#!/bin/bash

# Revolutionary LMS Platform Deployment Script

set -e

echo "🚀 Starting deployment of Revolutionary LMS Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set environment
export COMPOSE_PROJECT_NAME=revolutionary-lms

# Build and start services
echo "🔧 Building Docker images..."
docker-compose build

echo "🗄️ Running database migrations..."
docker-compose run --rm web python lms_platform/manage.py migrate

echo "📦 Collecting static files..."
docker-compose run --rm web python lms_platform/manage.py collectstatic --noinput

echo "🌐 Starting services..."
docker-compose up -d

echo "✅ Deployment complete!"
echo "🌟 Revolutionary LMS Platform is now running!"
echo "📊 Dashboard: http://localhost:8000/admin"
echo "📚 API: http://localhost:8000/api"
echo "🔮 Quantum Portal: http://localhost:8000/quantum"
echo "🧠 Neural Interface: http://localhost:8000/neural"
echo "⏰ Time Travel: http://localhost:8000/temporal"
echo "🌌 Metaverse: http://localhost:8000/metaverse"

echo "📋 Check logs with: docker-compose logs -f"
echo "🛑 Stop services with: docker-compose down"
