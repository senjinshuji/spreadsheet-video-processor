from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MediaType(str, Enum):
    VIDEO = "video"
    IMAGE = "image"
    AUTO = "auto"

class OutputFormat(str, Enum):
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    WEBM = "webm"

class MediaItem(BaseModel):
    url: str = Field(..., description="URL or path to the media file")
    duration: float = Field(..., description="Duration in seconds")
    start_time: float = Field(0, description="Start time for trimming (seconds)")
    media_type: MediaType = Field(MediaType.AUTO, description="Type of media")
    
class OutputSettings(BaseModel):
    format: OutputFormat = Field(OutputFormat.MP4)
    fps: int = Field(30, ge=1, le=120)
    resolution: Optional[str] = Field(None, description="Output resolution (e.g., '1920x1080')")
    codec: str = Field("libx264")
    audio_codec: str = Field("aac")
    quality: str = Field("high", description="Quality preset: low, medium, high")

class JobCreate(BaseModel):
    media_items: List[MediaItem]
    output_settings: OutputSettings = Field(default_factory=OutputSettings)
    metadata: Optional[Dict[str, Any]] = Field(None)

class SpreadsheetRow(BaseModel):
    row_number: int
    media_items: List[MediaItem]
    output_name: Optional[str] = None

class BatchProcessRequest(BaseModel):
    spreadsheet_id: str
    sheet_name: Optional[str] = None
    rows: List[SpreadsheetRow]
    output_settings: OutputSettings = Field(default_factory=OutputSettings)

class JobStatus(BaseModel):
    status: ProcessingStatus
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None
    output_url: Optional[str] = None
    error: Optional[str] = None

class JobResponse(BaseModel):
    job_id: str
    status: ProcessingStatus
    created_at: datetime
    updated_at: datetime
    user_id: str
    media_items: List[MediaItem]
    output_settings: OutputSettings
    progress: int = Field(0, ge=0, le=100)
    message: Optional[str] = None
    output_url: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None