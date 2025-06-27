#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def test_video_processing():
    print("Testing video processing API...")
    
    # Test data matching the spreadsheet format
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4",
                    "start_time": 0,
                    "duration": 3,
                    "media_type": "video"
                },
                {
                    "url": "https://test-videos.co.uk/vids/bigbuckbunny/mp4/h264/360/Big_Buck_Bunny_360_10s_1MB.mp4", 
                    "start_time": 5,
                    "duration": 2,
                    "media_type": "video"
                }
            ]
        }],
        "output_settings": {
            "fps": 30,
            "codec": "libx264",
            "quality": "medium"
        }
    }
    
    # Create batch jobs
    print("\nCreating batch job...")
    response = requests.post(f"{API_URL}/api/v1/jobs/batch", json=test_data)
    
    if response.status_code != 200:
        print(f"Error creating job: {response.status_code} - {response.text}")
        return
        
    jobs = response.json()
    print(f"Created {len(jobs)} job(s)")
    
    for job in jobs:
        job_id = job['job_id']
        print(f"\nJob ID: {job_id}")
        print(f"Status: {job['status']}")
        print(f"Mode: {job.get('mode', 'unknown')}")
        
        # Poll for job completion
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
            if response.status_code != 200:
                print(f"Error getting job status: {response.status_code}")
                break
                
            job_status = response.json()
            status = job_status['status']
            progress = job_status.get('progress', 0)
            message = job_status.get('message', '')
            
            print(f"\r[{attempt+1}/{max_attempts}] Status: {status} | Progress: {progress}% | {message}", end='')
            
            if status in ['completed', 'failed']:
                print()  # New line
                if status == 'completed':
                    print(f"Job completed successfully!")
                    print(f"Output URL: {job_status.get('output_url', 'N/A')}")
                    
                    # Test download endpoint
                    download_url = f"{API_URL}{job_status['output_url']}"
                    print(f"Testing download from: {download_url}")
                    
                    download_response = requests.get(download_url)
                    if download_response.status_code == 200:
                        content_type = download_response.headers.get('content-type', '')
                        if 'video' in content_type:
                            print("✓ Successfully downloaded video file")
                        else:
                            print(f"Response type: {content_type}")
                            if 'json' in content_type:
                                print(f"Response: {download_response.json()}")
                else:
                    print(f"Job failed: {job_status.get('error', 'Unknown error')}")
                break
                
            attempt += 1
            time.sleep(2)
        else:
            print(f"\nTimeout waiting for job completion")

if __name__ == "__main__":
    test_video_processing()