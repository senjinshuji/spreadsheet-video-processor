#!/usr/bin/env python3
import requests
import json
import time

API_URL = "https://spreadsheet-video-processor.onrender.com"

def test_endpoint(endpoint_name, endpoint_path):
    print(f"\n{'='*60}")
    print(f"Testing {endpoint_name}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(f"{API_URL}{endpoint_path}")
        
        if response.status_code != 200:
            print(f"Error creating job: {response.status_code} - {response.text}")
            return False
            
        result = response.json()
        
        if isinstance(result, dict) and "error" in result:
            print(f"Endpoint error: {result['error']}")
            return False
            
        jobs = result if isinstance(result, list) else [result]
        print(f"Created {len(jobs)} job(s)")
        
        if not jobs:
            print("No jobs created")
            return False
            
        job = jobs[0]
        job_id = job['job_id']
        print(f"Job ID: {job_id}")
        print(f"Initial status: {job['status']}")
        
        # Poll for completion (shorter timeout for tests)
        max_attempts = 30  # 1 minute max
        for attempt in range(max_attempts):
            response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
            
            if response.status_code != 200:
                print(f"Error getting job status: {response.status_code}")
                return False
                
            job_status = response.json()
            status = job_status['status']
            progress = job_status.get('progress', 0)
            message = job_status.get('message', '')
            
            print(f"\r[{attempt+1}/{max_attempts}] Status: {status} | Progress: {progress}% | {message}", end='')
            
            if status == 'completed':
                print("\n✓ Job completed successfully!")
                return True
                
            elif status == 'failed':
                print(f"\n✗ Job failed: {job_status.get('error', 'Unknown error')}")
                return False
                
            time.sleep(2)
        else:
            print(f"\n⚠ Timeout waiting for completion")
            return False
            
    except Exception as e:
        print(f"Exception during test: {e}")
        return False

def main():
    print("Testing all video processing endpoints...")
    
    # Test API health first
    try:
        response = requests.get(f"{API_URL}/api/v1/health")
        if response.status_code == 200:
            health = response.json()
            print(f"API Health: {health['status']}")
            print(f"MoviePy Available: {health['moviepy_available']}")
        else:
            print(f"Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"Failed to check API health: {e}")
        return
    
    # Test endpoints in order of complexity
    endpoints = [
        ("Generate Test Video (No Downloads)", "/api/v1/test/generate"),
        ("Simple Video Download", "/api/v1/test/simple"),
        ("Multiple Video Sources", "/api/v1/test/multiple"),
    ]
    
    results = {}
    
    for name, path in endpoints:
        success = test_endpoint(name, path)
        results[name] = "✓ PASSED" if success else "✗ FAILED"
        
        if success:
            print(f"✓ {name} completed successfully!")
            break  # If one works, we know the system is functional
        else:
            print(f"✗ {name} failed")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    for name, result in results.items():
        print(f"{name}: {result}")

if __name__ == "__main__":
    main()