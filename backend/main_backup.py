from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Optional, Dict
import uuid
import os
from datetime import datetime
from config import settings
from models import (
    JobCreate, JobStatus, JobResponse, ProcessingStatus,
    MediaItem, BatchProcessRequest
)
from storage import StorageManager
from auth import get_current_user, User
from celery_app import process_video_task
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    openapi_url=f"{settings.api_prefix}/openapi.json",
    docs_url=f"{settings.api_prefix}/docs"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage
storage = StorageManager()

# In-memory job storage (replace with database in production)
jobs_db: Dict[str, JobResponse] = {}

@app.get("/")
async def root():
    return {"message": "Spreadsheet Video Processor API", "version": settings.api_version}

@app.post(f"{settings.api_prefix}/auth/google")
async def google_auth(token: str):
    """Authenticate with Google OAuth token from Apps Script"""
    # TODO: Implement Google OAuth validation
    # For now, return a dummy token
    return {
        "access_token": "dummy-token",
        "token_type": "bearer"
    }

@app.post(f"{settings.api_prefix}/jobs/create", response_model=JobResponse)
async def create_job(
    job_data: JobCreate,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a new video processing job"""
    job_id = str(uuid.uuid4())
    
    job = JobResponse(
        job_id=job_id,
        status=ProcessingStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        user_id=current_user.id if current_user else "anonymous",
        media_items=job_data.media_items,
        output_settings=job_data.output_settings,
        progress=0,
        message="Job created successfully"
    )
    
    jobs_db[job_id] = job
    
    # Queue the processing task
    process_video_task.delay(job_id, job_data.dict())
    
    return job

@app.post(f"{settings.api_prefix}/jobs/batch", response_model=List[JobResponse])
async def create_batch_jobs(
    batch_request: BatchProcessRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create multiple video processing jobs from spreadsheet rows"""
    jobs = []
    
    for row_data in batch_request.rows:
        job_id = str(uuid.uuid4())
        
        # Convert row data to media items
        media_items = []
        for item in row_data.media_items:
            media_items.append(MediaItem(
                url=item.url,
                duration=item.duration,
                start_time=item.start_time,
                media_type=item.media_type
            ))
        
        job = JobResponse(
            job_id=job_id,
            status=ProcessingStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            user_id=current_user.id if current_user else "anonymous",
            media_items=media_items,
            output_settings=batch_request.output_settings,
            progress=0,
            message=f"Job created for row {row_data.row_number}",
            metadata={
                "row_number": row_data.row_number,
                "output_name": row_data.output_name or f"row_{row_data.row_number}_output"
            }
        )
        
        jobs_db[job_id] = job
        jobs.append(job)
        
        # Queue the processing task
        process_video_task.delay(job_id, {
            "media_items": [item.dict() for item in media_items],
            "output_settings": batch_request.output_settings.dict()
        })
    
    return jobs

@app.get(f"{settings.api_prefix}/jobs/{{job_id}}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get job status and details"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    # Check if user has access
    if current_user and job.user_id != current_user.id and job.user_id != "anonymous":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return job

@app.get(f"{settings.api_prefix}/jobs/{{job_id}}/download")
async def download_result(
    job_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Download the processed video"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    
    # Check if user has access
    if current_user and job.user_id != current_user.id and job.user_id != "anonymous":
        raise HTTPException(status_code=403, detail="Access denied")
    
    if job.status != ProcessingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Job not completed")
    
    if not job.output_url:
        raise HTTPException(status_code=404, detail="Output file not found")
    
    # Get file from storage
    file_path = storage.get_file_path(job.output_url)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        filename=f"processed_video_{job_id}.mp4"
    )

@app.post(f"{settings.api_prefix}/upload/media")
async def upload_media(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Upload a media file (video or image)"""
    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.allowed_video_extensions and ext not in settings.allowed_image_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Check file size
    contents = await file.read()
    if len(contents) > settings.max_file_size:
        raise HTTPException(status_code=400, detail="File too large")
    
    # Save file
    file_id = str(uuid.uuid4())
    file_key = f"media/{file_id}{ext}"
    
    url = await storage.save_file(file_key, contents)
    
    return {
        "url": url,
        "file_id": file_id,
        "filename": file.filename,
        "size": len(contents)
    }

@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

# Update job status endpoint (called by Celery worker)
@app.put(f"{settings.api_prefix}/jobs/{{job_id}}/status")
async def update_job_status(
    job_id: str,
    status_update: JobStatus
):
    """Update job status (internal use by workers)"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs_db[job_id]
    job.status = status_update.status
    job.progress = status_update.progress
    job.message = status_update.message
    job.updated_at = datetime.utcnow()
    
    if status_update.output_url:
        job.output_url = status_update.output_url
    
    if status_update.error:
        job.error = status_update.error
    
    return job

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)