#!/bin/bash
set -e

echo "Starting build process..."

# Update package list
echo "Updating package list..."
apt-get update

# Install system dependencies
echo "Installing system dependencies..."
apt-get install -y ffmpeg imagemagick

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Build process completed successfully!"