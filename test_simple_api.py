#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def test_simple_video():
    print("Testing simple video processing...")
    
    # Call the simple test endpoint
    response = requests.post(f"{API_URL}/api/v1/test/simple")
    
    if response.status_code != 200:
        print(f"Error creating job: {response.status_code} - {response.text}")
        return
        
    jobs = response.json()
    print(f"Created {len(jobs)} job(s)")
    
    if not jobs:
        print("No jobs created")
        return
        
    job = jobs[0]
    job_id = job['job_id']
    print(f"\nJob ID: {job_id}")
    print(f"Initial status: {job['status']}")
    
    # Poll for completion
    max_attempts = 60  # 2 minutes max
    for attempt in range(max_attempts):
        response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
        
        if response.status_code != 200:
            print(f"Error getting job status: {response.status_code}")
            break
            
        job_status = response.json()
        status = job_status['status']
        progress = job_status.get('progress', 0)
        message = job_status.get('message', '')
        
        print(f"\r[{attempt+1}/{max_attempts}] Status: {status} | Progress: {progress}% | {message}", end='')
        
        if status == 'completed':
            print("\n✓ Job completed successfully!")
            print(f"Output URL: {job_status.get('output_url', 'N/A')}")
            
            # Try to download
            if job_status.get('output_url'):
                download_url = f"{API_URL}{job_status['output_url']}"
                print(f"\nTesting download: {download_url}")
                
                download_response = requests.get(download_url)
                print(f"Download status: {download_response.status_code}")
                print(f"Content-Type: {download_response.headers.get('content-type', 'N/A')}")
                
                if download_response.status_code == 200:
                    if 'video' in download_response.headers.get('content-type', ''):
                        print("✓ Video file downloaded successfully")
                        print(f"File size: {len(download_response.content)} bytes")
                    else:
                        print(f"Response: {download_response.text[:500]}")
            break
            
        elif status == 'failed':
            print(f"\n✗ Job failed: {job_status.get('error', 'Unknown error')}")
            break
            
        time.sleep(2)
    else:
        print("\n✗ Timeout waiting for job completion")

if __name__ == "__main__":
    test_simple_video()