from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Dict, List
import uuid
from datetime import datetime
import os
import logging
from pathlib import Path
import time

# Conditional import of video processor
try:
    from video_processor import VideoProcessor
    video_processor = VideoProcessor()
    MOVIEPY_AVAILABLE = True
except ImportError as e:
    print(f"MoviePy not available: {e}")
    video_processor = None
    MOVIEPY_AVAILABLE = False

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

@app.get("/")
async def root():
    return {
        "message": "Video Processor API is running!",
        "status": "ok",
        "moviepy_available": MOVIEPY_AVAILABLE
    }

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "moviepy_available": MOVIEPY_AVAILABLE
    }

def process_video_job_mock(job_id: str, media_items: List[dict], output_settings: dict):
    """Mock video processing for when MoviePy is not available"""
    try:
        # Update job status
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["progress"] = 50
        jobs_db[job_id]["message"] = "Processing videos (mock mode)"
        
        # Simulate processing
        time.sleep(2)
        
        # Update job completion
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["output_url"] = f"/api/v1/jobs/{job_id}/download"
        jobs_db[job_id]["message"] = "Processing completed (mock mode - MoviePy not available)"
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        jobs_db[job_id]["status"] = "failed"
        jobs_db[job_id]["error"] = str(e)
        jobs_db[job_id]["completed_at"] = datetime.utcnow().isoformat()

def process_video_job_real(job_id: str, media_items: List[dict], output_settings: dict):
    """Real video processing with MoviePy"""
    try:
        # Update job status
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["progress"] = 0
        
        # Prepare media files for processing
        media_files = []
        
        for i, item in enumerate(media_items):
            media_files.append({
                "path": item["url"],
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
            "output_settings": data.get("output_settings", {}),
            "mode": "real" if MOVIEPY_AVAILABLE else "mock"
        }
        
        jobs_db[job_id] = job
        jobs.append(job)
        
        # Queue background processing
        if MOVIEPY_AVAILABLE:
            background_tasks.add_task(
                process_video_job_real,
                job_id,
                row.get("media_items", []),
                data.get("output_settings", {})
            )
        else:
            background_tasks.add_task(
                process_video_job_mock,
                job_id,
                row.get("media_items", []),
                data.get("output_settings", {})
            )
    
    return jobs

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@app.get("/api/v1/jobs/{job_id}/download")
async def download_job_output(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    if MOVIEPY_AVAILABLE and "output_file" in job:
        # Real file download
        output_file = job.get("output_file")
        file_path = os.path.join(STORAGE_PATH, output_file)
        if os.path.exists(file_path):
            return FileResponse(
                file_path,
                media_type="video/mp4",
                filename=f"processed_video_{job_id}.mp4"
            )
    
    # Mock response
    return {
        "message": "MoviePy is not available or file not found. This is a mock response.",
        "job_id": job_id,
        "download_url": f"https://example.com/mock-video-{job_id}.mp4"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)