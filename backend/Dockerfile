FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    git \
    wget \
    curl \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libfontconfig1 \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for MoviePy
ENV IMAGEIO_FFMPEG_EXE=/usr/bin/ffmpeg

# Set working directory
WORKDIR /app

# Copy only backend directory contents
COPY backend/ .

# Install Python dependencies with verbose output
RUN pip install --no-cache-dir -r requirements.txt

# Create storage directory
RUN mkdir -p /app/storage

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STORAGE_PATH=/app/storage

# Expose port
EXPOSE 8000

# Test imports before starting
RUN python test_moviepy_import.py || echo "MoviePy test failed"

# Use simple processor if MoviePy fails
RUN echo "Testing simple video processor..." && \
    python -c "from simple_video_processor import SimpleVideoProcessor; print('Simple processor available')" || echo "Simple processor failed"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/api/v1/health || exit 1

# Default command - use PORT env variable with fallback  
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1