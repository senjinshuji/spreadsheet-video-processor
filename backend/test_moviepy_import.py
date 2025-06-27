#!/usr/bin/env python3
"""Test MoviePy import with detailed error reporting"""

print("Python version:")
import sys
print(sys.version)

print("\nTesting MoviePy import...")

try:
    print("1. Testing imageio...")
    import imageio
    print("   ✓ imageio imported")
    
    print("2. Testing numpy...")
    import numpy
    print("   ✓ numpy imported")
    
    print("3. Testing PIL...")
    from PIL import Image
    print("   ✓ PIL imported")
    
    print("4. Testing moviepy.config...")
    from moviepy.config import check
    print("   ✓ moviepy.config imported")
    
    print("5. Testing moviepy.editor...")
    from moviepy.editor import VideoFileClip
    print("   ✓ moviepy.editor imported")
    
    print("\n✅ All imports successful!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    
print("\nChecking ffmpeg...")
import subprocess
try:
    result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
    print(f"FFmpeg: {result.stdout.split('\\n')[0]}")
except Exception as e:
    print(f"FFmpeg error: {e}")