#!/usr/bin/env python3
"""Test MoviePy imports to find the correct import method"""

print("Testing MoviePy imports...")

# Test 1: Traditional import
try:
    from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
    print("✓ Success: from moviepy.editor import ...")
except ImportError as e:
    print(f"✗ Failed: from moviepy.editor import ... - {e}")

# Test 2: Direct moviepy import
try:
    import moviepy
    print(f"✓ Success: import moviepy - version: {moviepy.__version__ if hasattr(moviepy, '__version__') else 'unknown'}")
    print(f"  Available attributes: {[attr for attr in dir(moviepy) if not attr.startswith('_')][:10]}...")
except ImportError as e:
    print(f"✗ Failed: import moviepy - {e}")

# Test 3: From moviepy directly
try:
    from moviepy import VideoFileClip, ImageClip, concatenate_videoclips
    print("✓ Success: from moviepy import ...")
except ImportError as e:
    print(f"✗ Failed: from moviepy import ... - {e}")

# Test 4: Check moviepy structure
try:
    import moviepy
    if hasattr(moviepy, 'video'):
        print("✓ Found moviepy.video module")
        if hasattr(moviepy.video, 'VideoClip'):
            print("  - Found moviepy.video.VideoClip")
        if hasattr(moviepy.video, 'io'):
            print("  - Found moviepy.video.io module")
except Exception as e:
    print(f"Error checking moviepy structure: {e}")

# Test 5: Alternative imports
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    print("✓ Success: from moviepy.video.io.VideoFileClip import VideoFileClip")
except ImportError as e:
    print(f"✗ Failed: moviepy.video.io.VideoFileClip - {e}")

try:
    from moviepy.video.VideoClip import ImageClip
    print("✓ Success: from moviepy.video.VideoClip import ImageClip")
except ImportError as e:
    print(f"✗ Failed: moviepy.video.VideoClip - {e}")

try:
    from moviepy.video.compositing.concatenate import concatenate_videoclips
    print("✓ Success: from moviepy.video.compositing.concatenate import concatenate_videoclips")
except ImportError as e:
    print(f"✗ Failed: moviepy.video.compositing.concatenate - {e}")

# Test 6: Check if we need to import specific modules
try:
    import moviepy.config
    print(f"✓ MoviePy config found")
except ImportError as e:
    print(f"✗ MoviePy config not found - {e}")