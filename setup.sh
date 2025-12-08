#!/bin/bash
# Setup script for Responsible AI Demo

echo "========================================"
echo "Responsible AI Demo - Setup Script"
echo "========================================"

echo ""
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi
echo "✅ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
echo "✅ Docker Compose found"

# Check jq (optional but recommended)
if ! command -v jq &> /dev/null; then
    echo "⚠️  jq not found. Installing recommended for better output formatting."
    echo "   Install with: sudo apt-get install jq (Ubuntu/Debian)"
    echo "   or: brew install jq (macOS)"
fi

echo ""
echo "Setting up project..."

# Create .env if not exists
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo "✅ .env created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
    echo "   nano .env"
    echo ""
else
    echo "✅ .env already exists"
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p data config dashboards tests docs app

echo "✅ Directories created"

# Make test scripts executable
if [ -d tests ]; then
    chmod +x tests/*.sh 2>/dev/null
    echo "✅ Test scripts made executable"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"

echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file and add your OPENAI_API_KEY:"
echo "   nano .env"
echo ""
echo "2. Start the services:"
echo "   docker-compose up -d"
echo ""
echo "3. Wait ~30 seconds for services to start"
echo ""
echo "4. Verify services are running:"
echo "   docker-compose ps"
echo "   curl http://localhost:8000/health"
echo ""
echo "5. Run the quickstart test:"
echo "   ./tests/step2_test_chatbot.sh"
echo ""
echo "6. Open the documentation:"
echo "   - README.md for full overview"
echo "   - QUICKSTART.md for fast start"
echo "   - docs/ folder for step-by-step guides"
echo ""
echo "7. Access the dashboards:"
echo "   - API: http://localhost:8000/docs"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "Happy monitoring! 🚀"
