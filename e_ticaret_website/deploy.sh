#!/bin/bash

# Production Deployment Script
echo "🚀 Starting deployment..."

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Build and start services
echo "🐳 Building and starting Docker services..."
docker-compose --env-file .env.prod up -d --build

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose --env-file .env.prod exec web python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
docker-compose --env-file .env.prod exec web python manage.py collectstatic --noinput

# Show running services
echo "✅ Deployment complete! Running services:"
docker-compose --env-file .env.prod ps

echo "🌐 Your site is live!"