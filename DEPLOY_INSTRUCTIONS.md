# Deployment Instructions - Final Steps

## 1. Update Google Apps Script with your Render URL

1. Go to your Render dashboard (https://dashboard.render.com)
2. Find your deployed service "video-processor-api"
3. Copy the service URL (it will look like: `https://video-processor-api-XXXX.onrender.com`)
4. Open the file `/gas/Code.gs` in your project
5. Replace line 4:
   ```javascript
   const API_BASE_URL = 'https://YOUR-RENDER-SERVICE.onrender.com/api/v1';
   ```
   With your actual URL:
   ```javascript
   const API_BASE_URL = 'https://video-processor-api-XXXX.onrender.com/api/v1';
   ```

## 2. Deploy Google Apps Script

1. Open Google Sheets where you want to use this tool
2. Go to Extensions → Apps Script
3. Delete any existing code
4. Copy all content from `/gas/Code.gs`
5. Paste it into the Apps Script editor
6. Save the project (give it a name like "Video Processor")
7. Run the `onOpen` function once to authorize permissions
8. Reload your Google Sheet

## 3. Configure Column Mappings

After the menu appears in your sheet:
1. Click "🎥 Video Processor" → "Settings"
2. Configure the column numbers according to your spreadsheet format:
   - 実行対象 column: 1
   - 実行結果 column: 2
   - First 素材 column: 3

## 4. Test the Integration

1. Add a test row with:
   - 実行対象: ○
   - 素材①: URL to a video/image
   - 使用開始: 0:00
   - 使用秒数: 5
2. Select the row
3. Click "🎥 Video Processor" → "Process Selected Rows"

## Current Status

✅ API is deployed and running at your Render URL
✅ Basic endpoints are working
⚠️ Video processing is currently mocked (returns example URLs)

## Next Steps for Full Implementation

When you're ready to add actual video processing:
1. We'll implement the video processing logic using MoviePy
2. Set up proper file storage (local or S3)
3. Configure Celery workers for async processing

For now, the integration is set up and you can test the workflow!