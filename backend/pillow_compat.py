"""Pillow compatibility patch for MoviePy"""
import PIL.Image

# Pillow 10.0.0 removed ANTIALIAS, replaced with LANCZOS
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
    
# Also add Resampling enum for newer Pillow versions
if hasattr(PIL.Image, 'Resampling'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS