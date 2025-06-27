# Google Sheets Integration Test

## Current Status
- ✅ API deployed and running at https://spreadsheet-video-processor.onrender.com
- ✅ API responds with mock video processing (MoviePy not yet available)
- ✅ Google Apps Script deployed with correct API URL
- 🔄 Docker rebuild in progress with additional MoviePy dependencies

## Test Instructions

1. Open your Google Spreadsheet
2. Click on the "🎥 Video Processor" menu
3. Select "Process All Marked Rows" or select specific rows and use "Process Selected Rows"
4. The script will:
   - Find rows with ○ marks
   - Send them to the API for processing
   - Monitor job status
   - Write result URLs in the 実行結果 column

## Expected Results
- Currently: Mock URLs like `https://example.com/mock-video-{job-id}.mp4`
- After MoviePy fix: Real download URLs like `/api/v1/jobs/{job-id}/download`

## API Endpoints
- Health Check: https://spreadsheet-video-processor.onrender.com/api/v1/health
- Root: https://spreadsheet-video-processor.onrender.com/
- Batch Jobs: POST https://spreadsheet-video-processor.onrender.com/api/v1/jobs/batch
- Job Status: GET https://spreadsheet-video-processor.onrender.com/api/v1/jobs/{job_id}
- Download: GET https://spreadsheet-video-processor.onrender.com/api/v1/jobs/{job_id}/download

## Monitoring Docker Rebuild
The Docker container is being rebuilt with additional dependencies for MoviePy.
You can monitor the deployment at: https://dashboard.render.com/