#!/bin/bash
# Quick Start Script for AlKabry Ecommerce

echo "======================================"
echo "AlKabry Ecommerce - Quick Start"
echo "======================================"
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.10+ first."
    exit 1
fi

echo "✓ Python found: $(python --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q
echo "✓ Dependencies installed"
echo ""

# Run migrations
echo "🗄️  Running migrations..."
python manage.py makemigrations --quiet
python manage.py migrate --quiet
echo "✓ Migrations complete"
echo ""

# Seed data
echo "🌱 Seeding database with sample data..."
python manage.py seed_data --users 30 --products 80 --reviews 200 --interactions 500
echo ""

# Start server
echo ""
echo "🚀 Starting development server..."
echo "======================================"
echo "📍 Visit: http://localhost:8000"
echo ""
echo "👤 Admin Credentials:"
echo "   Email: admin@alkabry.com"
echo "   Password: admin123"
echo ""
echo "👥 User Credentials:"
echo "   Email: user0@example.com"
echo "   Password: password123"
echo ""
echo "📊 Run Algorithm Comparison:"
echo "   python manage.py compare_algorithms"
echo "======================================"
echo ""

python manage.py runserver
