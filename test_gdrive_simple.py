#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def test_single_gdrive():
    """Test single Google Drive file"""
    
    # Test with one of your Google Drive URLs
    test_data = {
        "rows": [{
            "row_number": 1,
            "media_items": [
                {
                    "url": "https://drive.google.com/file/d/1FrmCNRhI3kgQWEukOWNSV_CRShDIippT/view?usp=drive_link",
                    "start_time": 5,  # 0:05 = 5 seconds
                    "duration": 5,   # 0:05 = 5 seconds
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
    
    print("Testing single Google Drive file...")
    print("URL: https://drive.google.com/file/d/1FrmCNRhI3kgQWEukOWNSV_CRShDIippT/view?usp=drive_link")
    
    response = requests.post(f"{API_URL}/api/v1/jobs/batch", json=test_data)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
        
    jobs = response.json()
    job = jobs[0]
    job_id = job['job_id']
    print(f"\nJob ID: {job_id}")
    
    # Monitor with timeout for stuck downloads
    last_message = ""
    stuck_count = 0
    
    for i in range(120):  # 4 minutes max
        response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
        if response.status_code == 200:
            status = response.json()
            current_message = status.get('message', '')
            progress = status.get('progress', 0)
            
            if current_message != last_message:
                print(f"\n[{i+1}] Status: {status['status']}")
                print(f"Progress: {progress}%")
                print(f"Message: {current_message}")
                last_message = current_message
                stuck_count = 0
            else:
                stuck_count += 1
                if stuck_count < 10:
                    print(".", end='', flush=True)
                elif stuck_count == 10:
                    print(f"\nJob stuck at: {current_message}")
                    print("This might indicate a download timeout or permission issue")
                elif stuck_count % 15 == 0:  # Every 30 seconds
                    print(f"\nStill stuck at: {current_message} (Progress: {progress}%)")
            
            if status['status'] in ['completed', 'failed']:
                print(f"\n\nFinal status: {status['status']}")
                if status.get('error'):
                    print(f"Error: {status['error']}")
                if status.get('output_url'):
                    print(f"Output: {API_URL}{status['output_url']}")
                break
                
        time.sleep(2)
    else:
        print(f"\n\nTimeout after 4 minutes")

if __name__ == "__main__":
    test_single_gdrive()