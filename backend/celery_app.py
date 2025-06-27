from celery import Celery
from config import settings
import logging
import os
import tempfile
from typing import List, Dict
from video_processor import VideoProcessor
from storage import StorageManager
import httpx
import asyncio

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "video_processor",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour
    task_soft_time_limit=3300,  # 55 minutes
)

storage = StorageManager()
video_processor = VideoProcessor()

async def update_job_status(job_id: str, status: str, progress: int, message: str, output_url: str = None, error: str = None):
    """Update job status via API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.put(
                f"http://localhost:8000{settings.api_prefix}/jobs/{job_id}/status",
                json={
                    "status": status,
                    "progress": progress,
                    "message": message,
                    "output_url": output_url,
                    "error": error
                }
            )
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Failed to update job status: {e}")

def sync_update_job_status(*args, **kwargs):
    """Synchronous wrapper for update_job_status"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(update_job_status(*args, **kwargs))
    finally:
        loop.close()

@celery_app.task(bind=True, name="process_video_task")
def process_video_task(self, job_id: str, job_data: Dict):
    """Process video concatenation task"""
    try:
        # Update status to processing
        sync_update_job_status(job_id, "processing", 10, "Starting video processing...")
        
        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download media files
            media_files = []
            total_items = len(job_data["media_items"])
            
            for idx, item in enumerate(job_data["media_items"]):
                progress = 10 + int((idx / total_items) * 30)
                sync_update_job_status(
                    job_id, "processing", progress, 
                    f"Downloading media file {idx + 1}/{total_items}..."
                )
                
                # Download file
                local_path = os.path.join(temp_dir, f"media_{idx}{os.path.splitext(item['url'])[1]}")
                
                # If URL is from our storage, get local path
                if item['url'].startswith('/storage/'):
                    local_path = storage.get_file_path(item['url'])
                else:
                    # Download from external URL
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        local_path = loop.run_until_complete(
                            storage.download_file(item['url'], local_path)
                        )
                    finally:
                        loop.close()
                
                media_files.append({
                    "path": local_path,
                    "duration": item["duration"],
                    "start_time": item.get("start_time", 0),
                    "media_type": item.get("media_type", "auto")
                })
            
            # Process videos
            sync_update_job_status(job_id, "processing", 50, "Processing media files...")
            
            output_path = os.path.join(temp_dir, f"output_{job_id}.mp4")
            
            # Process with progress callback
            def progress_callback(progress: int, message: str):
                actual_progress = 50 + int(progress * 0.4)  # 50-90%
                sync_update_job_status(job_id, "processing", actual_progress, message)
            
            video_processor.process_media_files(
                media_files,
                output_path,
                job_data["output_settings"],
                progress_callback
            )
            
            # Upload result
            sync_update_job_status(job_id, "processing", 90, "Uploading processed video...")
            
            output_key = f"outputs/{job_id}/output.mp4"
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                with open(output_path, 'rb') as f:
                    output_url = loop.run_until_complete(
                        storage.save_file(output_key, f.read())
                    )
            finally:
                loop.close()
            
            # Update job as completed
            sync_update_job_status(
                job_id, "completed", 100, 
                "Video processing completed successfully!",
                output_url=output_url
            )
            
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        sync_update_job_status(
            job_id, "failed", 0, 
            "Video processing failed",
            error=str(e)
        )
        raise

# Worker configuration
if __name__ == "__main__":
    celery_app.start()