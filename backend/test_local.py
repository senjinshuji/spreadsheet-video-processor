#!/usr/bin/env python3
"""
Local test script for video processing
"""
import requests
import time
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test basic API connection"""
    print("Testing API connection...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_video_processing():
    """Test video processing with sample videos"""
    print("Testing video processing...")
    
    # Create test job
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
    
    # Create job
    response = requests.post(f"{BASE_URL}/api/v1/jobs/batch", json=test_data)
    if response.status_code != 200:
        print(f"Error creating job: {response.text}")
        return
    
    jobs = response.json()
    job_id = jobs[0]["job_id"]
    print(f"Created job: {job_id}")
    
    # Monitor job status
    while True:
        response = requests.get(f"{BASE_URL}/api/v1/jobs/{job_id}")
        job = response.json()
        
        print(f"Status: {job['status']} - Progress: {job.get('progress', 0)}% - {job.get('message', '')}")
        
        if job['status'] in ['completed', 'failed']:
            break
            
        time.sleep(2)
    
    if job['status'] == 'completed':
        print(f"\nJob completed! Download URL: {BASE_URL}{job['output_url']}")
    else:
        print(f"\nJob failed: {job.get('error', 'Unknown error')}")

if __name__ == "__main__":
    test_api_connection()
    test_video_processing()