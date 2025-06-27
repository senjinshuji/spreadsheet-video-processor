#!/usr/bin/env python3
import requests
import json

API_URL = "https://spreadsheet-video-processor.onrender.com"

def check_gdrive_urls():
    """Check if Google Drive URLs are accessible"""
    
    urls = [
        "https://drive.google.com/file/d/1FrmCNRhI3kgQWEukOWNSV_CRShDIippT/view?usp=drive_link",
        "https://drive.google.com/file/d/1ffa4dIbHSmx85ai0pBgU5LRxZByDTRpF/view?usp=drive_link"
    ]
    
    for i, url in enumerate(urls, 1):
        print(f"\n=== Testing URL {i} ===")
        print(f"URL: {url}")
        
        try:
            response = requests.post(f"{API_URL}/api/v1/test/gdrive-check", json={"url": url})
            
            if response.status_code == 200:
                result = response.json()
                
                if "error" in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"Original URL: {result['original_url']}")
                    print(f"Converted URL: {result['converted_url']}")
                    print(f"Status Code: {result['status_code']}")
                    print(f"Content Type: {result.get('content_type', 'N/A')}")
                    print(f"Content Length: {result.get('content_length', 'N/A')}")
                    print(f"Accessible: {'✅ Yes' if result['accessible'] else '❌ No'}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    check_gdrive_urls()