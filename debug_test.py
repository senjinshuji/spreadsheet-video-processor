#!/usr/bin/env python3
"""Debug test to check media_info structure"""

# Test data structure
test_data = {
    "rows": [{
        "row_number": 1,
        "media_items": [
            {
                "url": "https://drive.google.com/file/d/1ffa4dIbHSmx85ai0pBgU5LRxZByDTRpF/view?usp=drive_link",
                "start_time": 0,
                "duration": 5,
                "media_type": "video"
            }
        ]
    }],
    "output_settings": {
        "fps": 24,
        "codec": "libx264",
        "quality": "low",
        "resolution": "640x360"
    }
}

# Simulate what happens in main.py
for row in test_data.get("rows", []):
    media_items = row.get("media_items", [])
    print(f"Row {row.get('row_number')}: {len(media_items)} media items")
    
    # Simulate process_video_job_real
    media_files = []
    for i, item in enumerate(media_items):
        print(f"\nOriginal item {i}:")
        print(f"  Keys: {list(item.keys())}")
        print(f"  URL: {item.get('url')}")
        print(f"  Duration: {item.get('duration')}")
        print(f"  Start time: {item.get('start_time')}")
        
        media_file = {
            "url": item["url"],  # This should work
            "duration": item.get("duration", 5),
            "start_time": item.get("start_time", 0),
            "media_type": item.get("media_type", "auto")
        }
        media_files.append(media_file)
        print(f"  Created media_file: {media_file}")
    
    # Simulate video_processor
    print("\n--- In video_processor ---")
    for idx, media_info in enumerate(media_files):
        print(f"\nProcessing media {idx}:")
        print(f"  Keys: {list(media_info.keys())}")
        print(f"  media_info: {media_info}")
        
        file_path = media_info.get("path") or media_info.get("url")
        print(f"  file_path: {file_path}")
        
        if not file_path:
            print(f"  ERROR: No file path or URL found!")
            print(f"  path value: {media_info.get('path')}")
            print(f"  url value: {media_info.get('url')}")