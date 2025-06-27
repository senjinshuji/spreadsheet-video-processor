#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def test_minimal():
    """Test with minimal configuration"""
    print("Testing minimal video processing...")
    
    # Very simple test - single short video
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "start_time": 0,
                    "duration": 1,  # Just 1 second
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
    
    print("Creating job...")
    response = requests.post(f"{API_URL}/api/v1/jobs/batch", json=test_data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
        
    jobs = response.json()
    if not jobs:
        print("No jobs created")
        return
        
    job = jobs[0]
    job_id = job['job_id']
    print(f"Job ID: {job_id}")
    
    # Monitor for shorter time
    for i in range(30):  # 1 minute max
        response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
        if response.status_code == 200:
            status = response.json()
            print(f"\r[{i+1}/30] Status: {status['status']} | Progress: {status.get('progress', 0)}% | {status.get('message', '')}", end='')
            
            if status['status'] == 'completed':
                print("\n✅ Success!")
                return
            elif status['status'] == 'failed':
                print(f"\n❌ Failed: {status.get('error', 'Unknown error')}")
                return
                
        time.sleep(2)
    
    print("\n⏰ Timeout")

if __name__ == "__main__":
    test_minimal()