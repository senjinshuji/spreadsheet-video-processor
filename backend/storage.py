import os
import aiofiles
import httpx
from typing import Optional
import boto3
from minio import Minio
from config import settings
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self):
        self.backend = settings.storage_backend
        
        if self.backend == "s3":
            self.s3_client = boto3.client(
                's3',
                endpoint_url=settings.s3_endpoint,
                aws_access_key_id=settings.s3_access_key,
                aws_secret_access_key=settings.s3_secret_key,
                region_name=settings.s3_region
            )
        elif self.backend == "minio":
            self.minio_client = Minio(
                settings.s3_endpoint.replace("http://", "").replace("https://", ""),
                access_key=settings.s3_access_key,
                secret_key=settings.s3_secret_key,
                secure=settings.s3_endpoint.startswith("https")
            )
            # Ensure bucket exists
            if not self.minio_client.bucket_exists(settings.s3_bucket):
                self.minio_client.make_bucket(settings.s3_bucket)
        else:  # local storage
            os.makedirs(settings.storage_path, exist_ok=True)
    
    async def save_file(self, key: str, content: bytes) -> str:
        """Save file and return URL"""
        if self.backend == "local":
            file_path = os.path.join(settings.storage_path, key)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(content)
            
            return f"/storage/{key}"
        
        elif self.backend == "s3":
            self.s3_client.put_object(
                Bucket=settings.s3_bucket,
                Key=key,
                Body=content
            )
            return f"s3://{settings.s3_bucket}/{key}"
        
        elif self.backend == "minio":
            import io
            self.minio_client.put_object(
                settings.s3_bucket,
                key,
                io.BytesIO(content),
                len(content)
            )
            return f"minio://{settings.s3_bucket}/{key}"
    
    def get_file_path(self, url: str) -> str:
        """Get local file path from URL"""
        if url.startswith("/storage/"):
            return os.path.join(settings.storage_path, url[9:])
        return url
    
    async def download_file(self, url: str, destination: str) -> str:
        """Download file from URL to local path"""
        if url.startswith("/storage/"):
            # Local file
            source = self.get_file_path(url)
            import shutil
            shutil.copy2(source, destination)
            return destination
        
        elif url.startswith("s3://"):
            # S3 file
            parts = url[5:].split("/", 1)
            bucket = parts[0]
            key = parts[1]
            self.s3_client.download_file(bucket, key, destination)
            return destination
        
        elif url.startswith("minio://"):
            # MinIO file
            parts = url[8:].split("/", 1)
            bucket = parts[0]
            key = parts[1]
            self.minio_client.fget_object(bucket, key, destination)
            return destination
        
        else:
            # External URL
            async with httpx.AsyncClient() as client:
                response = await client.get(url, follow_redirects=True)
                response.raise_for_status()
                
                async with aiofiles.open(destination, 'wb') as f:
                    await f.write(response.content)
                
                return destination


class GoogleDriveStorage:
    """Google Drive storage handler for uploading processed videos"""
    
    def __init__(self, credentials_path: Optional[str] = None):
        self.credentials_path = credentials_path or os.getenv("GOOGLE_DRIVE_CREDENTIALS")
        self.folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")  # Target folder ID
        self.service = None
        
    def authenticate(self):
        """Authenticate with Google Drive API"""
        try:
            if not self.credentials_path or not os.path.exists(self.credentials_path):
                logger.warning("Google Drive credentials not found, upload will be skipped")
                return False
                
            # Load service account credentials
            with open(self.credentials_path, 'r') as f:
                credentials_info = json.load(f)
            
            from google.oauth2 import service_account
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            
            from googleapiclient.discovery import build
            self.service = build('drive', 'v3', credentials=credentials)
            return True
            
        except Exception as e:
            logger.error(f"Failed to authenticate with Google Drive: {e}")
            return False
    
    def upload_video(self, file_path: str, filename: str) -> Optional[str]:
        """Upload video to Google Drive and return shareable URL"""
        if not self.service and not self.authenticate():
            return None
            
        try:
            from googleapiclient.http import MediaFileUpload
            
            # File metadata
            file_metadata = {
                'name': filename,
                'parents': [self.folder_id] if self.folder_id else []
            }
            
            # Media upload
            media = MediaFileUpload(
                file_path,
                mimetype='video/mp4',
                resumable=True
            )
            
            # Upload file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            
            # Make file shareable (anyone with link can view)
            permission = {
                'type': 'anyone',
                'role': 'reader'
            }
            
            self.service.permissions().create(
                fileId=file_id,
                body=permission
            ).execute()
            
            # Return shareable URL
            shareable_url = f"https://drive.google.com/file/d/{file_id}/view?usp=drive_link"
            logger.info(f"Successfully uploaded {filename} to Google Drive: {shareable_url}")
            
            return shareable_url
            
        except Exception as e:
            logger.error(f"Failed to upload {filename} to Google Drive: {e}")
            return None