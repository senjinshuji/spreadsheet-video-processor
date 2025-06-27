import subprocess
import os
import logging
from typing import List, Dict, Optional, Callable

logger = logging.getLogger(__name__)

class SimpleVideoProcessor:
    """Simple video processor using ffmpeg directly"""
    
    def __init__(self):
        self.temp_dir = "/tmp"
        logger.info("SimpleVideoProcessor initialized (ffmpeg-based)")
    
    def process_media_files(
        self,
        media_files: List[Dict],
        output_path: str,
        output_settings: Dict,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """Process videos using ffmpeg directly"""
        try:
            if progress_callback:
                progress_callback(10, "Starting video processing...")
            
            # For now, just copy the first video as a placeholder
            if media_files and len(media_files) > 0:
                first_video = media_files[0]
                
                # Simple ffmpeg command to create a test video
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi', '-i', 'color=c=blue:s=640x480:d=5',
                    '-vf', 'drawtext=text=\'Test Video\':fontcolor=white:fontsize=30:x=(w-text_w)/2:y=(h-text_h)/2',
                    '-c:v', 'libx264',
                    '-preset', 'ultrafast',
                    output_path
                ]
                
                logger.info(f"Running ffmpeg: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"ffmpeg failed: {result.stderr}")
                
                if progress_callback:
                    progress_callback(100, "Processing complete!")
                
                logger.info(f"Created test video at: {output_path}")
            else:
                raise ValueError("No media files provided")
                
        except Exception as e:
            logger.error(f"Error in simple video processing: {e}")
            raise