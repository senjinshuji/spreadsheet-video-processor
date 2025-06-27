#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def test_google_drive():
    print("Testing Google Drive URL processing...")
    print("URL: https://drive.google.com/file/d/1ffa4dIbHSmx85ai0pBgU5LRxZByDTRpF/view?usp=drive_link")
    
    # Test health first
    try:
        health_response = requests.get(f"{API_URL}/api/v1/health")
        if health_response.status_code == 200:
            health = health_response.json()
            print(f"API Status: {health['status']}")
            print(f"MoviePy Available: {health['moviepy_available']}")
        else:
            print(f"Health check failed: {health_response.status_code}")
            return
    except Exception as e:
        print(f"Failed to check API health: {e}")
        return
    
    # Test Google Drive endpoint
    try:
        print("\nCalling /api/v1/test/gdrive...")
        response = requests.post(f"{API_URL}/api/v1/test/gdrive")
        
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            return
            
        result = response.json()
        
        if isinstance(result, dict) and "error" in result:
            print(f"Error: {result['error']}")
            return
            
        jobs = result if isinstance(result, list) else [result]
        print(f"✓ Created {len(jobs)} job(s)")
        
        if not jobs:
            print("No jobs created")
            return
            
        job = jobs[0]
        job_id = job['job_id']
        print(f"Job ID: {job_id}")
        print(f"Status: {job['status']}")
        
        # Monitor progress
        print("\nMonitoring job progress...")
        max_attempts = 90  # 3 minutes for download
        
        for attempt in range(max_attempts):
            try:
                status_response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
                
                if status_response.status_code != 200:
                    print(f"\nError getting status: {status_response.status_code}")
                    break
                    
                job_status = status_response.json()
                status = job_status['status']
                progress = job_status.get('progress', 0)
                message = job_status.get('message', '')
                
                print(f"\r[{attempt+1:2d}/{max_attempts}] {status:12s} | {progress:3d}% | {message}", end='', flush=True)
                
                if status == 'completed':
                    print("\n\n🎉 Google Drive video processing completed!")
                    
                    output_url = job_status.get('output_url')
                    if output_url:
                        print(f"Output URL: {output_url}")
                        
                        # Test download
                        download_url = f"{API_URL}{output_url}"
                        print(f"\nTesting download: {download_url}")
                        
                        download_response = requests.get(download_url)
                        print(f"Download status: {download_response.status_code}")
                        
                        if download_response.status_code == 200:
                            content_type = download_response.headers.get('content-type', '')
                            content_size = len(download_response.content)
                            
                            print(f"Content-Type: {content_type}")
                            print(f"File size: {content_size:,} bytes")
                            
                            if 'video' in content_type and content_size > 0:
                                print("✅ Successfully processed Google Drive video!")
                            else:
                                print(f"⚠️  Unexpected content")
                        else:
                            print(f"❌ Download failed: {download_response.text}")
                    break
                    
                elif status == 'failed':
                    print(f"\n\n❌ Job failed: {job_status.get('error', 'Unknown error')}")
                    break
                    
                time.sleep(2)
                
            except Exception as e:
                print(f"\nError during monitoring: {e}")
                break
        else:
            print(f"\n\n⏰ Timeout after {max_attempts * 2} seconds")
            
    except Exception as e:
        print(f"Exception during test: {e}")

if __name__ == "__main__":
    test_google_drive()