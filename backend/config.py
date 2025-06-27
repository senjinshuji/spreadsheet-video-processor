from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    api_title: str = "Spreadsheet Video Processor API"
    api_version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth2
    google_client_id: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # Storage
    storage_backend: str = os.getenv("STORAGE_BACKEND", "local")  # local, s3, minio
    storage_path: str = os.getenv("STORAGE_PATH", "./storage")
    
    # S3/MinIO settings
    s3_endpoint: Optional[str] = os.getenv("S3_ENDPOINT")
    s3_access_key: Optional[str] = os.getenv("S3_ACCESS_KEY")
    s3_secret_key: Optional[str] = os.getenv("S3_SECRET_KEY")
    s3_bucket: str = os.getenv("S3_BUCKET", "video-processor")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    
    # Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Processing
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    allowed_video_extensions: set = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm"}
    allowed_image_extensions: set = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"}
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "https://script.google.com",
        "*"  # Allow all origins in development
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()