"""MoviePy configuration"""
import os

# Set FFmpeg path if needed
# MoviePy should auto-detect ffmpeg in PATH, but we can help it
os.environ['IMAGEIO_FFMPEG_EXE'] = 'ffmpeg'

# Enable verbose logging for debugging
os.environ['MOVIEPY_DEBUG'] = '1'