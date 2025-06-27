#!/usr/bin/env python3
import requests
import json

# Test both local and production APIs
apis = {
    "local": "http://localhost:8000",
    "production": "https://spreadsheet-video-processor.onrender.com"
}

for env, base_url in apis.items():
    print(f"\n{'='*50}")
    print(f"Testing {env} API at {base_url}")
    print(f"{'='*50}")
    
    try:
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"MoviePy available: {data.get('moviepy_available', 'Not specified')}")
        else:
            print(f"Error: {response.text}")
            
        # Test health endpoint
        response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        print(f"\nHealth endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2)}")
            
    except requests.exceptions.ConnectionError:
        print(f"Connection error - {env} API is not reachable")
    except requests.exceptions.Timeout:
        print(f"Timeout - {env} API is not responding")
    except Exception as e:
        print(f"Error: {e}")