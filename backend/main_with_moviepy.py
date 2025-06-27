from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Dict, List
import uuid
from datetime import datetime
import os
import tempfile
import logging
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor

from video_processor import VideoProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Processor API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory storage
jobs_db: Dict[str, dict] = {}

# Storage paths
STORAGE_PATH = os.getenv("STORAGE_PATH", "/tmp/video-processor")
Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)

# Thread pool for video processing
executor = ThreadPoolExecutor(max_workers=4)

# Video processor instance
video_processor = VideoProcessor()

@app.get("/")
async def root():
    return {"message": "Video Processor API is running!", "status": "ok"}

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/test/process")
async def test_process(background_tasks: BackgroundTasks):
    """Test endpoint with sample video URLs"""
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
                    "start_time": 0,
                    "duration": 3
                },
                {
                    "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
                    "start_time": 5,
                    "duration": 2
                }
            ]
        }],
        "output_settings": {
            "fps": 30,
            "codec": "libx264",
            "quality": "medium"
        }
    }
    
    return await create_batch_jobs(background_tasks, test_data)

def process_video_job(job_id: str, media_items: List[dict], output_settings: dict):
    """Process video in background thread"""
    try:
        # Update job status
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["progress"] = 0
        
        # Prepare media files for processing
        media_files = []
        temp_files = []
        
        for i, item in enumerate(media_items):
            # For now, we'll simulate downloading by using the URL directly
            # In production, you'd download the file first
            media_files.append({
                "path": item["url"],  # In production, download to temp file
                "duration": item.get("duration", 5),
                "start_time": item.get("start_time", 0),
                "media_type": item.get("media_type", "auto")
            })
        
        # Output file path
        output_filename = f"{job_id}.mp4"
        output_path = os.path.join(STORAGE_PATH, output_filename)
        
        # Progress callback
        def update_progress(progress: int, message: str):
            jobs_db[job_id]["progress"] = progress
            jobs_db[job_id]["message"] = message
        
        # Process videos
        video_processor.process_media_files(
            media_files=media_files,
            output_path=output_path,
            output_settings=output_settings,
            progress_callback=update_progress
        )
        
        # Update job completion
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["output_url"] = f"/api/v1/jobs/{job_id}/download"
        jobs_db[job_id]["output_file"] = output_filename
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()

@app.post("/api/v1/jobs/batch")
async def create_batch_jobs(background_tasks: BackgroundTasks, data: dict):
    """Create batch video processing jobs"""
    jobs = []
    
    for i, row in enumerate(data.get("rows", [])):
        job_id = str(uuid.uuid4())
        
        # Create job entry
        job = {
            "job_id": job_id,
            "status": "pending",
            "progress": 0,
            "message": "Job queued for processing",
            "created_at": datetime.utcnow().isoformat(),
            "row_number": row.get("row_number", i + 1),
            "media_items": row.get("media_items", []),
            "output_settings": data.get("output_settings", {})
        }
        
        jobs_db[job_id] = job
        jobs.append(job)
        
        # Queue background processing
        background_tasks.add_task(
            process_video_job,
            job_id,
            row.get("media_items", []),
            data.get("output_settings", {})
        )
    
    return jobs

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs_db:
        # Return 404 properly for FastAPI
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@app.get("/api/v1/jobs/{job_id}/download")
async def download_job_output(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    # Get output file path
    output_file = job.get("output_file")
    if not output_file:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    file_path = os.path.join(STORAGE_PATH, output_file)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=f"processed_video_{job_id}.mp4"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)