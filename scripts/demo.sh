#!/usr/bin/env bash
set -e

echo "🚀 CookWithMe — Local Demo Script"
echo "================================"
echo ""

echo "1️⃣ Starting Docker stack..."
docker compose up -d --build

echo ""
echo "2️⃣ Waiting for backend to be ready..."
until curl -s http://localhost:8000/docs >/dev/null; do
  sleep 1
done

echo "✅ Backend is up!"

echo ""
echo "🌐 Open these URLs in your browser:"
echo "👉 Backend API docs:  http://localhost:8000/docs"
echo "👉 Frontend UI:       http://localhost:8501"

echo ""
echo "🧪 Suggested demo flow:"
echo "--------------------------------"
echo "1. Login as admin"
echo "2. Create a recipe"
echo "3. Browse recipe list"
echo "4. Add recipe to favorites"
echo "5. Open AI Recommendations"
echo "--------------------------------"

echo ""
echo "✅ Demo environment is ready 🎉"