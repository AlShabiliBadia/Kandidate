#!/bin/bash

# Kandidate - Quick Start Script

echo "🚀 Starting Kandidate ATS..."
echo ""

# Start all services
cd "$(dirname "$0")"
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
echo ""
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "✅ Kandidate is ready!"
echo ""
echo "📝 Access Points:"
echo "   Frontend: Open frontend/index.html in your browser"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   RabbitMQ: http://localhost:15672 (guest/guest)"
echo ""
echo "🔑 Admin Credentials:"
echo "   Email: admin@kandidate.com"
echo "   Password: admin123"
echo ""
echo "📚 See frontend/README.md for testing instructions"
echo ""
