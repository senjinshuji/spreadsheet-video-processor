FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    git \
    wget \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgstreamer1.0-0 \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    gstreamer1.0-libav \
    gstreamer1.0-tools \
    && rm -rf /var/lib/apt/lists/*

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

# Test MoviePy import before starting
RUN python -c "from moviepy.editor import VideoFileClip; print('MoviePy imported successfully')" || echo "MoviePy import failed"

# Default command - use PORT env variable
CMD uvicorn main:app --host 0.0.0.0 --port $PORT