#!/bin/bash

echo "🚀 Setting up Spreadsheet Video Processor..."

# Check if Docker is available
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    echo "✅ Docker found. Using Docker setup..."
    
    # Copy environment file
    if [ ! -f backend/.env ]; then
        cp backend/.env.example backend/.env
        echo "📝 Created .env file. Please edit it with your settings."
    fi
    
    # Start services
    docker-compose up -d
    
    echo "🎉 Services started!"
    echo "📊 API: http://localhost:8000"
    echo "🌸 Flower (Celery monitor): http://localhost:5555"
    echo "📚 API Docs: http://localhost:8000/api/v1/docs"
    
else
    echo "🔧 Docker not found. Setting up manually..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required"
        exit 1
    fi
    
    # Check Redis
    if ! command -v redis-server &> /dev/null; then
        echo "❌ Redis is required. Install with:"
        echo "   Ubuntu/WSL: sudo apt install redis-server"
        echo "   macOS: brew install redis"
        echo "   Windows: Download from https://redis.io/download"
        exit 1
    fi
    
    # Check FFmpeg
    if ! command -v ffmpeg &> /dev/null; then
        echo "❌ FFmpeg is required. Install with:"
        echo "   Ubuntu/WSL: sudo apt install ffmpeg"
        echo "   macOS: brew install ffmpeg"
        echo "   Windows: Download from https://ffmpeg.org/download.html"
        exit 1
    fi
    
    cd backend
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    pip install -r requirements.txt
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.example .env
        echo "📝 Created .env file. Please edit it with your settings."
    fi
    
    echo "🎉 Setup complete!"
    echo ""
    echo "To start the services:"
    echo "1. Start Redis: redis-server"
    echo "2. Start API: cd backend && source venv/bin/activate && python main.py"
    echo "3. Start Worker: cd backend && source venv/bin/activate && celery -A celery_app worker --loglevel=info"
fi

echo ""
echo "📋 Next steps:"
echo "1. Open Google Sheets"
echo "2. Go to Extensions → Apps Script"
echo "3. Copy the code from gas/ folder"
echo "4. Set API URL in Video Processor → Settings"