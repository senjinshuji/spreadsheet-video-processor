#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def debug_stuck_job():
    """Debug why job is stuck at 25%"""
    
    # Create a simple test job
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://www.w3schools.com/html/mov_bbb.mp4",
                    "start_time": 0,
                    "duration": 2,
                    "media_type": "video"
                },
                {
                    "url": "https://www.w3schools.com/html/mov_bbb.mp4", 
                    "start_time": 5,
                    "duration": 2,
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
    
    print("Creating test job...")
    response = requests.post(f"{API_URL}/api/v1/jobs/batch", json=test_data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
        
    jobs = response.json()
    job = jobs[0]
    job_id = job['job_id']
    print(f"Job ID: {job_id}")
    
    # Monitor with detailed info
    last_progress = -1
    last_message = ""
    stuck_count = 0
    
    for i in range(60):  # 2 minutes
        response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
        if response.status_code == 200:
            status = response.json()
            current_progress = status.get('progress', 0)
            current_message = status.get('message', '')
            
            # Print if progress or message changed
            if current_progress != last_progress or current_message != last_message:
                print(f"\n[{i+1}] Status: {status['status']}")
                print(f"Progress: {current_progress}%")
                print(f"Message: {current_message}")
                
                if status.get('error'):
                    print(f"Error: {status['error']}")
                
                last_progress = current_progress
                last_message = current_message
                stuck_count = 0
            else:
                stuck_count += 1
                print(".", end='', flush=True)
                
                # If stuck for 10 checks (20 seconds), print full status
                if stuck_count >= 10:
                    print(f"\n\nJob appears stuck. Full status:")
                    print(json.dumps(status, indent=2))
                    stuck_count = 0
            
            if status['status'] in ['completed', 'failed']:
                print(f"\n\nFinal status: {status['status']}")
                if status.get('error'):
                    print(f"Error details: {status['error']}")
                break
                
        time.sleep(2)

if __name__ == "__main__":
    debug_stuck_job()