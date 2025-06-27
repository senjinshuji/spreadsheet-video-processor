#!/usr/bin/env python3
import requests
import json
import sys

API_URL = "https://spreadsheet-video-processor.onrender.com"

def get_job_details(job_id):
    """Get detailed job status"""
    try:
        response = requests.get(f"{API_URL}/api/v1/jobs/{job_id}")
        if response.status_code == 200:
            job = response.json()
            print(f"Job ID: {job_id}")
            print(f"Status: {job.get('status')}")
            print(f"Progress: {job.get('progress')}%")
            print(f"Message: {job.get('message')}")
            print(f"Error: {job.get('error', 'None')}")
            print(f"Created: {job.get('created_at')}")
            print(f"Completed: {job.get('completed_at', 'Not yet')}")
            print(f"\nFull job data:")
            print(json.dumps(job, indent=2))
        else:
            print(f"Error getting job: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        job_id = sys.argv[1]
        get_job_details(job_id)
    else:
        # Create a simple test job
        print("Creating test job...")
        response = requests.post(f"{API_URL}/api/v1/test/generate")
        if response.status_code == 200:
            jobs = response.json()
            if jobs and len(jobs) > 0:
                job_id = jobs[0]['job_id']
                print(f"Created job: {job_id}")
                get_job_details(job_id)
            else:
                print("No job created")
        else:
            print(f"Error creating job: {response.status_code}")