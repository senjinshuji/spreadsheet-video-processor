import os
from typing import List, Dict, Callable, Optional

# Apply Pillow compatibility patch before importing MoviePy
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips
from PIL import Image
import numpy as np
import logging
import requests
import tempfile
import time
from urllib.parse import urlparse
from pathlib import Path

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.supported_video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm'}
        self.supported_image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
        self.temp_dir = tempfile.gettempdir()
    
    def detect_media_type(self, file_path: str) -> str:
        """Detect if file is video or image based on extension"""
        ext = Path(file_path).suffix.lower()
        if ext in self.supported_video_extensions:
            return "video"
        elif ext in self.supported_image_extensions:
            return "image"
        else:
            # Try to detect by attempting to open as video
            try:
                VideoFileClip(file_path).close()
                return "video"
            except:
                return "image"
    
    def process_video(self, file_path: str, duration: float, start_time: float = 0) -> VideoFileClip:
        """Process video file with trimming"""
        try:
            # Validate inputs
            if duration is None:
                raise ValueError(f"Duration is None for video: {file_path}")
            if start_time is None:
                start_time = 0
                
            logger.info(f"Processing video: {file_path}, duration={duration}, start_time={start_time}")
            
            # Check if file exists first
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Video file not found: {file_path}")
                
            file_size = os.path.getsize(file_path)
            logger.info(f"Video file size: {file_size} bytes")
            
            clip = VideoFileClip(file_path)
            
            # Validate and trim video
            video_duration = clip.duration
            logger.info(f"Original video duration: {video_duration}s, requested start: {start_time}s, duration: {duration}s")
            
            if start_time >= video_duration:
                # If start time exceeds video duration, create a black screen
                logger.warning(f"Start time {start_time}s exceeds video duration {video_duration}s, creating black screen")
                clip.close()
                from moviepy.editor import ColorClip
                clip = ColorClip(size=(640, 480), color=(0, 0, 0), duration=duration)
            else:
                # Calculate actual end time
                end_time = min(start_time + duration, video_duration)
                actual_duration = end_time - start_time
                
                # Trim video
                clip = clip.subclip(start_time, end_time)
                
                # If requested duration is longer than available, extend with black screen
                if actual_duration < duration:
                    remaining_duration = duration - actual_duration
                    logger.info(f"Extending video with {remaining_duration}s of black screen")
                    
                    from moviepy.editor import ColorClip, concatenate_videoclips
                    black_clip = ColorClip(size=clip.size, color=(0, 0, 0), duration=remaining_duration)
                    clip = concatenate_videoclips([clip, black_clip])
            
            logger.info(f"Processed video: {file_path} (duration: {clip.duration}s)")
            return clip
            
        except Exception as e:
            logger.error(f"Error processing video {file_path}: {e}")
            raise
    
    def process_image(self, file_path: str, duration: float, fps: int = 30) -> ImageClip:
        """Convert image to video clip with specified duration"""
        try:
            # Open and convert image
            img = Image.open(file_path)
            if img.mode == 'RGBA':
                # Convert RGBA to RGB
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            
            # Create video clip from image
            clip = ImageClip(np.array(img), duration=duration)
            clip = clip.set_fps(fps)
            
            logger.info(f"Processed image: {file_path} (duration: {duration}s)")
            return clip
            
        except Exception as e:
            logger.error(f"Error processing image {file_path}: {e}")
            raise
    
    def convert_google_drive_url(self, url: str) -> str:
        """Convert Google Drive share URL to direct download URL"""
        if 'drive.google.com' in url and '/file/d/' in url:
            # Extract file ID from Google Drive URL
            # Format: https://drive.google.com/file/d/FILE_ID/view?usp=sharing
            try:
                file_id = url.split('/file/d/')[1].split('/')[0]
                direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                logger.info(f"Converted Google Drive URL: {url} -> {direct_url}")
                return direct_url
            except Exception as e:
                logger.warning(f"Failed to convert Google Drive URL {url}: {e}")
                return url
        return url

    def download_file(self, url: str, output_path: str) -> str:
        """Download file from URL with improved error handling"""
        try:
            # Convert Google Drive URLs to direct download format
            original_url = url
            url = self.convert_google_drive_url(url)
            
            logger.info(f"Downloading file from {url}")
            if url != original_url:
                logger.info(f"Original URL: {original_url}")
            
            # Parse URL
            parsed_url = urlparse(url)
            
            # Add headers to handle various servers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'video/*,image/*,*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'identity',  # Avoid compression issues
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache',
                'Connection': 'keep-alive',
            }
            
            # First, check with HEAD request
            session = requests.Session()
            session.headers.update(headers)
            
            try:
                head_response = session.head(url, timeout=30, allow_redirects=True)
                logger.info(f"HEAD request status: {head_response.status_code}")
                logger.info(f"HEAD final URL: {head_response.url}")
                logger.info(f"HEAD Content-Type: {head_response.headers.get('content-type', 'N/A')}")
                logger.info(f"HEAD Content-Length: {head_response.headers.get('content-length', 'N/A')}")
                
                content_type = head_response.headers.get('content-type', '')
                if 'text/html' in content_type.lower():
                    raise Exception(f"URL returns HTML page (Content-Type: {content_type})")
                    
            except Exception as e:
                logger.warning(f"HEAD request failed: {e}, proceeding with GET")
            
            # Special handling for specific domains
            if 'test-videos.co.uk' in parsed_url.netloc:
                headers['Referer'] = 'https://test-videos.co.uk/'
            elif 'drive.google.com' in parsed_url.netloc:
                # Google Drive specific headers
                headers.update({
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.9,ja;q=0.8',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Upgrade-Insecure-Requests': '1',
                })
            
            # Create session for better connection handling
            session = requests.Session()
            session.headers.update(headers)
            
            # Make request with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Shorter timeout for Google Drive to prevent hanging
                    timeout = 30 if 'drive.google.com' in url else 60
                    response = session.get(url, stream=True, timeout=timeout, allow_redirects=True)
                    response.raise_for_status()
                    
                    # Log final URL after redirects
                    final_url = response.url
                    logger.info(f"Final URL after redirects: {final_url}")
                    
                    # Check content type
                    content_type = response.headers.get('content-type', '')
                    logger.info(f"Content-Type: {content_type}")
                    
                    # Special handling for Google Drive download confirmation
                    if 'drive.google.com' in url and 'text/html' in content_type.lower():
                        # Check if this is a download confirmation page
                        first_chunk = next(response.iter_content(chunk_size=1024), b'')
                        response.close()
                        
                        if b'confirm=' in first_chunk or b'download_warning' in first_chunk:
                            logger.info("Google Drive download confirmation detected, extracting confirm link")
                            # Extract confirm token and retry
                            content_str = first_chunk.decode('utf-8', errors='ignore')
                            import re
                            confirm_match = re.search(r'confirm=([^&"]+)', content_str)
                            if confirm_match:
                                confirm_token = confirm_match.group(1)
                                confirm_url = f"{url}&confirm={confirm_token}"
                                logger.info(f"Retrying with confirm URL: {confirm_url}")
                                response = session.get(confirm_url, stream=True, timeout=60, allow_redirects=True)
                                response.raise_for_status()
                                content_type = response.headers.get('content-type', '')
                                logger.info(f"Confirmed download Content-Type: {content_type}")
                    
                    # Validate content type
                    if content_type and not any(media_type in content_type.lower() for media_type in ['video', 'octet-stream', 'mp4', 'mpeg', 'binary']):
                        if 'text/html' in content_type.lower():
                            logger.error(f"Received HTML page instead of video file. URL may be incorrect.")
                            logger.error(f"Response headers: {dict(response.headers)}")
                            raise Exception("URL points to HTML page, not video file")
                    
                    # Get file size
                    total_size = int(response.headers.get('content-length', 0))
                    logger.info(f"Expected file size: {total_size} bytes")
                    
                    # Download file
                    downloaded = 0
                    chunk_size = 8192
                    
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                
                                # Progress logging every 1MB
                                if downloaded % (1024 * 1024) < chunk_size:
                                    logger.info(f"Downloaded: {downloaded}/{total_size} bytes")
                    
                    # Verify download
                    actual_size = os.path.getsize(output_path)
                    logger.info(f"Downloaded {actual_size} bytes to {output_path}")
                    
                    if actual_size == 0:
                        raise Exception("Downloaded file is empty")
                    
                    if total_size > 0 and abs(actual_size - total_size) > 1024:  # Allow 1KB difference
                        logger.warning(f"Size mismatch: expected {total_size}, got {actual_size}")
                    
                    # Verify it's a valid media file
                    with open(output_path, 'rb') as f:
                        header = f.read(16)
                        logger.info(f"File header (hex): {header.hex()}")
                    
                    return output_path
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        except Exception as e:
            logger.error(f"Failed to download {url}: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            raise
    
    def normalize_clips(self, clips: List[VideoFileClip], target_resolution: Optional[str] = None) -> List[VideoFileClip]:
        """Normalize all clips to same resolution"""
        if not clips:
            return clips
        
        # Determine target resolution
        if target_resolution:
            width, height = map(int, target_resolution.split('x'))
        else:
            # Use the resolution of the first clip
            width, height = clips[0].size
        
        normalized_clips = []
        for clip in clips:
            if clip.size != (width, height):
                clip = clip.resize((width, height))
            normalized_clips.append(clip)
        
        return normalized_clips
    
    def process_media_files(
        self, 
        media_files: List[Dict],
        output_path: str,
        output_settings: Dict,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ):
        """Process multiple media files and concatenate them"""
        
        clips = []
        total_files = len(media_files)
        
        # Process each media file
        temp_files = []
        try:
            for idx, media_info in enumerate(media_files):
                # More granular progress reporting
                base_progress = int((idx / total_files) * 40)  # 0-40% for processing files
                if progress_callback:
                    progress_callback(base_progress, f"Starting file {idx + 1}/{total_files}")
                
                file_path = media_info.get("path") or media_info.get("url")
                if not file_path:
                    logger.error(f"Media info keys: {list(media_info.keys())}")
                    logger.error(f"Media info content: {media_info}")
                    raise ValueError(f"No file path or URL provided in media_info: {media_info}")
                
                duration = media_info.get("duration")
                if duration is None:
                    logger.error(f"Duration is None in media_info: {media_info}")
                    raise ValueError(f"Duration is required but was None for media item {idx}")
                
                # Convert to float if needed
                try:
                    duration = float(duration)
                except (TypeError, ValueError) as e:
                    logger.error(f"Invalid duration value: {duration}, type: {type(duration)}")
                    raise ValueError(f"Duration must be a number, got {duration} ({type(duration)})")
                
                start_time = media_info.get("start_time", 0)
                if start_time is None:
                    start_time = 0
                else:
                    try:
                        start_time = float(start_time)
                    except (TypeError, ValueError):
                        logger.error(f"Invalid start_time value: {start_time}")
                        start_time = 0
                        
                media_type = media_info.get("media_type", "auto")
                
                logger.info(f"Processing media {idx}: file_path={file_path}, duration={duration}, start_time={start_time}")
                
                # Download file if it's a URL
                if file_path.startswith(('http://', 'https://')):
                    # Extract filename from URL or use index
                    url_path = urlparse(file_path).path
                    if url_path:
                        filename = os.path.basename(url_path)
                        name, ext = os.path.splitext(filename)
                        if not ext:
                            ext = '.mp4'
                    else:
                        name = f"temp_{idx}"
                        ext = '.mp4'
                    
                    temp_file = os.path.join(self.temp_dir, f"{name}_{idx}{ext}")
                    logger.info(f"Downloading media {idx}: {file_path}")
                    logger.info(f"Saving to: {temp_file}")
                    
                    self.download_file(file_path, temp_file)
                    temp_files.append(temp_file)
                    file_path = temp_file
                    
                    # Verify downloaded file
                    if os.path.exists(temp_file):
                        file_size = os.path.getsize(temp_file)
                        logger.info(f"Downloaded file size: {file_size} bytes")
                        
                        # Test if file can be opened by MoviePy
                        try:
                            test_clip = VideoFileClip(temp_file)
                            test_duration = test_clip.duration
                            test_clip.close()
                            logger.info(f"File verified, duration: {test_duration}s")
                        except Exception as ve:
                            logger.error(f"Failed to verify video file: {ve}")
                            raise
                    else:
                        raise Exception(f"Downloaded file not found: {temp_file}")
                
                # Auto-detect media type if needed
                if media_type == "auto":
                    media_type = self.detect_media_type(file_path)
                
                # Process based on type
                if media_type == "video":
                    clip = self.process_video(file_path, duration, start_time)
                else:
                    clip = self.process_image(file_path, duration, output_settings.get("fps", 30))
                
                clips.append(clip)
                
                # Update progress after processing each file
                progress = int(((idx + 1) / total_files) * 40)  # Complete at 40%
                if progress_callback:
                    progress_callback(progress, f"Processed file {idx + 1}/{total_files}")
            
            if not clips:
                raise ValueError("No valid clips to process")
            
            # Normalize clips to same resolution
            if progress_callback:
                progress_callback(60, "Normalizing video dimensions...")
            
            clips = self.normalize_clips(clips, output_settings.get("resolution"))
            
            # Concatenate clips
            if progress_callback:
                progress_callback(70, "Concatenating clips...")
            
            final_clip = concatenate_videoclips(clips, method="compose")
            
            # Apply quality settings (optimized for faster encoding)
            quality_presets = {
                "low": {"bitrate": "500k", "preset": "ultrafast"},
                "medium": {"bitrate": "1M", "preset": "faster"},
                "high": {"bitrate": "2M", "preset": "fast"}
            }
            
            quality = output_settings.get("quality", "medium")
            preset_settings = quality_presets.get(quality, quality_presets["medium"])
            
            # Export video
            if progress_callback:
                progress_callback(80, "Encoding final video...")
            
            write_params = {
                "codec": output_settings.get("codec", "libx264"),
                "audio_codec": output_settings.get("audio_codec", "aac"),
                "fps": output_settings.get("fps", 30),
                "bitrate": preset_settings["bitrate"],
                "preset": preset_settings["preset"]
            }
            
            # Add audio parameter if there's no audio
            if not any(hasattr(clip, 'audio') and clip.audio for clip in clips):
                write_params["audio"] = False
            
            logger.info(f"Writing video with params: {write_params}")
            
            # Create progress callback for encoding
            def encoding_progress(current_frame, total_frames):
                if total_frames > 0:
                    encode_progress = int((current_frame / total_frames) * 20)  # 80-100%
                    if progress_callback:
                        progress_callback(80 + encode_progress, f"Encoding {int((current_frame / total_frames) * 100)}%")
            
            # Add progress callback if MoviePy version supports it
            try:
                final_clip.write_videofile(output_path, progress_bar=False, logger=None, **write_params)
            except Exception as e:
                logger.error(f"Error during video encoding: {e}")
                raise
            
            # Cleanup
            for clip in clips:
                clip.close()
            final_clip.close()
            
            if progress_callback:
                progress_callback(100, "Processing complete!")
            
            logger.info(f"Video processing complete: {output_path}")
            
        except Exception as e:
            logger.error(f"Error in process_media_files: {str(e)}")
            raise
        finally:
            # Cleanup temp files
            for temp_file in temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        logger.info(f"Cleaned up temp file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Failed to cleanup {temp_file}: {e}")