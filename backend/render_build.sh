#!/usr/bin/env bash
# Render build script

echo "Installing system dependencies..."
apt-get update
apt-get install -y ffmpeg imagemagick git

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Creating storage directory..."
mkdir -p /opt/render/project/storage

echo "Build complete!"