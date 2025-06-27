from fastapi import FastAPI, BackgroundTasks, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import Dict, List
import uuid
from datetime import datetime
import os
import logging
from pathlib import Path
import time

# Configure MoviePy before importing
try:
    import moviepy_config
except:
    pass

# Apply Pillow compatibility patch
try:
    import pillow_compat
except:
    pass

# Conditional import of video processor
try:
    print("Attempting to import video_processor...")
    from video_processor import VideoProcessor
    print("VideoProcessor imported successfully!")
    
    print("Creating VideoProcessor instance...")
    video_processor = VideoProcessor()
    print("VideoProcessor instance created successfully!")
    
    MOVIEPY_AVAILABLE = True
    print("✅ MoviePy imported successfully!")
except ImportError as e:
    print(f"❌ MoviePy ImportError: {e}")
    import traceback
    traceback.print_exc()
    video_processor = None
    MOVIEPY_AVAILABLE = False
except Exception as e:
    print(f"❌ Unexpected error importing MoviePy: {e}")
    print(f"Error type: {type(e)}")
    import traceback
    traceback.print_exc()
    video_processor = None
    MOVIEPY_AVAILABLE = False

print(f"MOVIEPY_AVAILABLE: {MOVIEPY_AVAILABLE}")

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

@app.head("/")
async def head_root():
    """HEAD request support for health checks"""
    return Response(status_code=200)

@app.get("/api/v1/health")
async def health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "moviepy_available": MOVIEPY_AVAILABLE
    }

@app.post("/api/v1/test/simple")
async def test_simple_process(background_tasks: BackgroundTasks):
    """Test with a direct video file URL"""
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://download.samplelib.com/mp4/sample-5s.mp4",
                    "start_time": 0,
                    "duration": 3,
                    "media_type": "video"
                }
            ]
        }],
        "output_settings": {
            "fps": 24,
            "codec": "libx264", 
            "quality": "low",
            "resolution": "480x360"
        }
    }
    
    return await create_batch_jobs(background_tasks, test_data)

@app.post("/api/v1/test/multiple")
async def test_multiple_sources(background_tasks: BackgroundTasks):
    """Test with multiple video sources"""
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://filesamples.com/samples/video/mp4/mp4_sample_1.mp4",
                    "start_time": 0,
                    "duration": 2,
                    "media_type": "video"
                },
                {
                    "url": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "start_time": 0,
                    "duration": 2,
                    "media_type": "video"
                }
            ]
        }],
        "output_settings": {
            "fps": 24,
            "codec": "libx264",
            "quality": "low",
            "resolution": "480x360"
        }
    }
    
    return await create_batch_jobs(background_tasks, test_data)

@app.post("/api/v1/test/generate")
async def test_generate_video(background_tasks: BackgroundTasks):
    """Test video generation without downloads - simplified"""
    # Use simple test URL instead of generating files
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "start_time": 0,
                    "duration": 1,
                    "media_type": "video"
                },
                {
                    "url": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "start_time": 3,
                    "duration": 1,
                    "media_type": "video"
                }
            ]
        }],
        "output_settings": {
            "fps": 24,
            "codec": "libx264",
            "quality": "low"
        }
    }
    
    return await create_batch_jobs(background_tasks, test_data)

@app.post("/api/v1/test/gdrive")
async def test_google_drive(background_tasks: BackgroundTasks):
    """Test with Google Drive URL"""
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://drive.google.com/file/d/1ffa4dIbHSmx85ai0pBgU5LRxZByDTRpF/view?usp=drive_link",
                    "start_time": 0,
                    "duration": 5,
                    "media_type": "video"
                }
            ]
        }],
        "output_settings": {
            "fps": 24,
            "codec": "libx264",
            "quality": "low",
            "resolution": "640x360"
        }
    }
    
    return await create_batch_jobs(background_tasks, test_data)

@app.post("/api/v1/test/gdrive-check")
async def check_google_drive_url(data: dict):
    """Check if Google Drive URL is accessible"""
    url = data.get("url")
    if not url:
        return {"error": "URL required"}
    
    try:
        from video_processor import VideoProcessor
        processor = VideoProcessor()
        
        # Convert URL
        converted_url = processor.convert_google_drive_url(url)
        
        # Try HEAD request
        import requests
        response = requests.head(converted_url, timeout=10)
        
        return {
            "original_url": url,
            "converted_url": converted_url,
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type'),
            "content_length": response.headers.get('content-length'),
            "accessible": response.status_code == 200
        }
    except Exception as e:
        return {"error": str(e)}

def process_video_job_mock(job_id: str, media_items: List[dict], output_settings: dict):
    """Mock video processing for when MoviePy is not available"""
    try:
        # Update job status
        jobs_db[job_id]["status"] = "processing"
        jobs_db[job_id]["progress"] = 50
        jobs_db[job_id]["message"] = "Processing videos (mock mode)"
        
        # Simulate processing
        time.sleep(2)
        
        # Create a test Google Drive URL (temporary for testing)
        test_drive_url = "https://drive.google.com/file/d/1test_file_id/view?usp=drive_link"
        
        # Update job completion
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["output_url"] = f"/api/v1/jobs/{job_id}/download"
        jobs_db[job_id]["gdrive_url"] = test_drive_url  # Test Google Drive URL
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
            # Get duration with proper None handling
            duration = item.get("duration")
            if duration is None:
                logger.warning(f"Duration is None for item {i}, using default 5 seconds")
                duration = 5
                
            # Get start_time with proper None handling
            start_time = item.get("start_time")
            if start_time is None:
                start_time = 0
                
            media_files.append({
                "url": item.get("url") or item.get("path"),  # Support both url and path
                "duration": duration,
                "start_time": start_time,
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
        
        # Try to upload to Google Drive
        drive_url = None
        try:
            from storage import GoogleDriveStorage
            drive_storage = GoogleDriveStorage()
            drive_url = drive_storage.upload_video(output_path, output_filename)
            if drive_url:
                logger.info(f"Successfully uploaded to Google Drive: {drive_url}")
        except Exception as e:
            logger.warning(f"Failed to upload to Google Drive: {e}")
        
        # Update job completion
        jobs_db[job_id]["status"] = "completed"
        jobs_db[job_id]["progress"] = 100
        jobs_db[job_id]["output_url"] = f"/api/v1/jobs/{job_id}/download"
        jobs_db[job_id]["output_file"] = output_filename
        jobs_db[job_id]["gdrive_url"] = drive_url  # Google Drive URL
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
        
        # Debug log for media items
        media_items = row.get("media_items", [])
        logger.info(f"Row {i}: {len(media_items)} media items")
        for j, item in enumerate(media_items):
            logger.info(f"  Item {j}: url={item.get('url')}, duration={item.get('duration')}, start_time={item.get('start_time')}")
        
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)