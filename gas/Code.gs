// Google Apps Script for Spreadsheet Video Processor
// This script adds a custom menu to Google Sheets for processing videos

const API_BASE_URL = 'https://spreadsheet-video-processor-docker.onrender.com/api/v1'; // Render API URL
const STORAGE_KEY = 'VIDEO_PROCESSOR_AUTH_TOKEN';

/**
 * Creates custom menu when spreadsheet opens
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🎥 Video Processor')
    .addItem('Process All Marked Rows', 'processAllMarkedRows')
    .addItem('Process Selected Rows', 'processSelectedRows')
    .addItem('Process Current Row', 'processCurrentRow')
    .addSeparator()
    .addItem('Debug: Check Selected Rows', 'debugCheckRows')
    .addItem('Test API Connection', 'testAPIConnection')
    .addItem('Settings', 'showSettings')
    .addItem('Help', 'showHelp')
    .addToUi();
}

/**
 * Process all rows with ○ mark in the entire sheet
 */
function processAllMarkedRows() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const lastRow = sheet.getLastRow();
  const config = getColumnConfig();
  
  // Find all rows with ○ mark
  const markedRows = [];
  for (let row = 2; row <= lastRow; row++) { // Start from row 2 (skip header)
    const targetValue = sheet.getRange(row, config.targetColumn).getValue();
    if (targetValue) {
      const valueStr = targetValue.toString().trim();
      if (valueStr === '○' || valueStr === 'o' || valueStr === 'O' || valueStr === '〇') {
        markedRows.push(row);
      }
    }
  }
  
  if (markedRows.length === 0) {
    SpreadsheetApp.getUi().alert('実行対象なし', 'シート全体に○マークのついた行がありません。\nA列に○を入力してから再度実行してください。', SpreadsheetApp.getUi().ButtonSet.OK);
    return;
  }
  
  // Show confirmation dialog
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert(
    '処理の確認',
    `シート全体で${markedRows.length}行が実行対象（○マーク）です。\n処理を開始しますか？`,
    ui.ButtonSet.YES_NO
  );
  
  if (response !== ui.Button.YES) {
    return;
  }
  
  // Process all marked rows
  processMarkedRows(markedRows);
}

/**
 * Process selected rows
 */
function processSelectedRows() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const selection = sheet.getActiveRange();
  
  if (!selection) {
    SpreadsheetApp.getUi().alert('Please select rows to process');
    return;
  }
  
  const startRow = selection.getRow();
  const numRows = selection.getNumRows();
  
  // First, check how many rows actually have ○ mark
  const config = getColumnConfig();
  let targetRowCount = 0;
  
  for (let i = 0; i < numRows; i++) {
    const row = startRow + i;
    const targetValue = sheet.getRange(row, config.targetColumn).getValue();
    // デバッグ用ログ
    console.log(`Row ${row}: targetValue = "${targetValue}", type = ${typeof targetValue}`);
    
    // より柔軟な○の判定
    if (targetValue) {
      const valueStr = targetValue.toString().trim();
      if (valueStr === '○' || valueStr === 'o' || valueStr === 'O' || valueStr === '〇') {
        targetRowCount++;
      }
    }
  }
  
  if (targetRowCount === 0) {
    SpreadsheetApp.getUi().alert('実行対象なし', '選択した範囲に○マークのついた行がありません。\nA列に○を入力してから再度実行してください。', SpreadsheetApp.getUi().ButtonSet.OK);
    return;
  }
  
  // Show confirmation dialog
  const ui = SpreadsheetApp.getUi();
  const response = ui.alert(
    '処理の確認',
    `選択範囲の${numRows}行中、${targetRowCount}行が実行対象（○マーク）です。\n処理を開始しますか？`,
    ui.ButtonSet.YES_NO
  );
  
  if (response !== ui.Button.YES) {
    return;
  }
  
  // Process rows
  processRows(startRow, numRows);
}

/**
 * Process current row
 */
function processCurrentRow() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const currentRow = sheet.getActiveCell().getRow();
  
  processRows(currentRow, 1);
}

/**
 * Process specific marked rows
 */
function processMarkedRows(markedRows) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const ui = SpreadsheetApp.getUi();
  
  // Get column configuration
  const config = getColumnConfig();
  
  // Validate configuration
  if (!validateConfig(config)) {
    ui.alert('Invalid Configuration', 'Please check your column mappings in Settings.', ui.ButtonSet.OK);
    return;
  }
  
  // Collect data from marked rows
  const rows = [];
  for (const row of markedRows) {
    const rowData = getRowData(sheet, row, config);
    
    if (rowData) {
      rows.push({
        row_number: row,
        media_items: rowData.media_items,
        output_name: rowData.output_name
      });
    }
  }
  
  if (rows.length === 0) {
    ui.alert('有効なデータなし', '○マークのある行に有効なデータが見つかりませんでした。', ui.ButtonSet.OK);
    return;
  }
  
  // Get output settings
  const outputSettings = getOutputSettings();
  
  // Create batch request
  const batchRequest = {
    spreadsheet_id: SpreadsheetApp.getActiveSpreadsheet().getId(),
    sheet_name: sheet.getName(),
    rows: rows,
    output_settings: outputSettings
  };
  
  // Send request to API
  try {
    const jobs = createBatchJobs(batchRequest);
    
    // Store job IDs and initial status in sheet
    storeJobIds(sheet, markedRows, jobs);
    
    // Show toast notification
    SpreadsheetApp.getActiveSpreadsheet().toast(
      `${jobs.length}件の動画を処理中`,
      '処理開始',
      3
    );
    
    // Start monitoring jobs
    monitorJobs(jobs);
    
    // Show processing notification
    SpreadsheetApp.getActiveSpreadsheet().toast(
      '処理中です。実行結果列で進捗を確認してください。',
      '処理開始',
      10
    );
    
  } catch (error) {
    ui.alert('Error', 'Failed to start processing: ' + error.message, ui.ButtonSet.OK);
  }
}

/**
 * Process specified rows
 */
function processRows(startRow, numRows) {
  const sheet = SpreadsheetApp.getActiveSheet();
  const ui = SpreadsheetApp.getUi();
  
  // Get column configuration
  const config = getColumnConfig();
  
  // Validate configuration
  if (!validateConfig(config)) {
    ui.alert('Invalid Configuration', 'Please check your column mappings in Settings.', ui.ButtonSet.OK);
    return;
  }
  
  // Collect data from rows
  const rows = [];
  const processedRows = [];
  for (let i = 0; i < numRows; i++) {
    const row = startRow + i;
    const rowData = getRowData(sheet, row, config);
    
    if (rowData) {
      rows.push({
        row_number: row,
        media_items: rowData.media_items,
        output_name: rowData.output_name
      });
      processedRows.push(row);
    }
  }
  
  if (rows.length === 0) {
    ui.alert('実行対象なし', '選択した範囲に○マークのついた行がありません。\nA列に○を入力してから再度実行してください。', ui.ButtonSet.OK);
    return;
  }
  
  // Get output settings
  const outputSettings = getOutputSettings();
  
  // Create batch request
  const batchRequest = {
    spreadsheet_id: SpreadsheetApp.getActiveSpreadsheet().getId(),
    sheet_name: sheet.getName(),
    rows: rows,
    output_settings: outputSettings
  };
  
  // Send request to API
  try {
    const jobs = createBatchJobs(batchRequest);
    
    // Store job IDs and initial status in sheet (only for rows with ○)
    storeJobIds(sheet, processedRows, jobs);
    
    // Show toast notification
    SpreadsheetApp.getActiveSpreadsheet().toast(
      `Processing ${jobs.length} video(s)`,
      'Started',
      3
    );
    
    // Start monitoring jobs
    monitorJobs(jobs);
    
    // Show simple processing notification instead of dialog
    SpreadsheetApp.getActiveSpreadsheet().toast(
      '処理中です。実行結果列で進捗を確認してください。',
      '処理開始',
      10
    );
    
  } catch (error) {
    ui.alert('Error', 'Failed to start processing: ' + error.message, ui.ButtonSet.OK);
  }
}

/**
 * Get row data for new spreadsheet format
 */
function getRowData(sheet, row, config) {
  const data = sheet.getRange(row, 1, 1, sheet.getLastColumn()).getValues()[0];
  
  // Check if this row should be processed (実行対象 column)
  const shouldProcess = data[config.targetColumn - 1];
  if (!shouldProcess) {
    return null; // Skip this row
  }
  
  // より柔軟な○の判定
  const processStr = shouldProcess.toString().trim();
  if (processStr !== '○' && processStr !== 'o' && processStr !== 'O' && processStr !== '〇') {
    return null; // Skip this row
  }
  
  // Parse media items from material columns
  const mediaItems = [];
  
  // Start from material column (素材①)
  let materialIndex = 1;
  let currentColumn = config.firstMaterialColumn;
  
  while (currentColumn <= data.length) {
    const materialUrl = data[currentColumn - 1]; // 素材URL
    const startTime = data[currentColumn]; // 使用開始
    const duration = data[currentColumn + 1]; // 使用秒数
    
    // If no URL, break the loop
    if (!materialUrl || materialUrl.toString().trim() === '') {
      break;
    }
    
    // Parse start time (format: m:ss or just seconds)
    let parsedStartTime = 0;
    if (startTime) {
      parsedStartTime = parseTimeFormat(startTime);
    }
    
    // Parse duration (format: m:ss or just seconds)
    let parsedDuration = 5; // default
    if (duration) {
      parsedDuration = parseTimeFormat(duration);
    }
    
    mediaItems.push({
      url: materialUrl.toString().trim(),
      duration: parsedDuration,
      start_time: parsedStartTime,
      media_type: 'auto'
    });
    
    // Move to next material (skip 3 columns: URL, start, duration)
    currentColumn += 3;
    materialIndex++;
  }
  
  if (mediaItems.length === 0) {
    return null;
  }
  
  return {
    media_items: mediaItems,
    output_name: `processed_row_${row}`
  };
}

/**
 * Get column configuration for new format
 */
function getColumnConfig() {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  return {
    targetColumn: parseInt(scriptProperties.getProperty('TARGET_COLUMN') || '1'), // 実行対象
    resultColumn: parseInt(scriptProperties.getProperty('RESULT_COLUMN') || '2'), // 実行結果
    firstMaterialColumn: parseInt(scriptProperties.getProperty('FIRST_MATERIAL_COLUMN') || '3'), // 素材①
    statusColumn: parseInt(scriptProperties.getProperty('STATUS_COLUMN') || '2') // 実行結果列をステータス表示に使用
  };
}

/**
 * Get output settings
 */
function getOutputSettings() {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  return {
    format: scriptProperties.getProperty('OUTPUT_FORMAT') || 'mp4',
    fps: parseInt(scriptProperties.getProperty('OUTPUT_FPS') || '30'),
    resolution: scriptProperties.getProperty('OUTPUT_RESOLUTION') || null,
    codec: scriptProperties.getProperty('OUTPUT_CODEC') || 'libx264',
    audio_codec: scriptProperties.getProperty('OUTPUT_AUDIO_CODEC') || 'aac',
    quality: scriptProperties.getProperty('OUTPUT_QUALITY') || 'high'
  };
}

/**
 * Validate column configuration
 */
function validateConfig(config) {
  return config.targetColumn > 0 && config.resultColumn > 0 && config.firstMaterialColumn > 0;
}

/**
 * Create batch jobs via API
 */
function createBatchJobs(batchRequest) {
  const token = getAuthToken();
  
  const response = UrlFetchApp.fetch(`${API_BASE_URL}/jobs/batch`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': token ? `Bearer ${token}` : ''
    },
    payload: JSON.stringify(batchRequest),
    muteHttpExceptions: true
  });
  
  if (response.getResponseCode() !== 200) {
    throw new Error('Failed to create jobs: ' + response.getContentText());
  }
  
  return JSON.parse(response.getContentText());
}

/**
 * Store job IDs in spreadsheet
 */
function storeJobIds(sheet, processedRows, jobs) {
  const config = getColumnConfig();
  
  for (let i = 0; i < jobs.length; i++) {
    const row = processedRows[i];
    const job = jobs[i];
    
    // Update status in result column
    sheet.getRange(row, config.resultColumn).setValue('Processing...');
    
    // Store job ID as note
    sheet.getRange(row, config.resultColumn).setNote(`Job ID: ${job.job_id}`);
  }
}

/**
 * Monitor jobs and update status
 */
function monitorJobs(jobs) {
  // Store job IDs for monitoring
  const cache = CacheService.getUserCache();
  const jobIds = jobs.map(job => job.job_id);
  cache.put('ACTIVE_JOBS', JSON.stringify(jobIds), 3600); // 1 hour
  
  // Set up trigger for monitoring
  ScriptApp.newTrigger('checkJobStatus')
    .timeBased()
    .everyMinutes(1)
    .create();
}

/**
 * Check job status (called by trigger)
 */
function checkJobStatus() {
  const cache = CacheService.getUserCache();
  const jobIdsStr = cache.get('ACTIVE_JOBS');
  
  if (!jobIdsStr) {
    // No active jobs, remove trigger
    removeTrigger('checkJobStatus');
    return;
  }
  
  const jobIds = JSON.parse(jobIdsStr);
  const sheet = SpreadsheetApp.getActiveSheet();
  const config = getColumnConfig();
  const token = getAuthToken();
  
  const activeJobs = [];
  
  for (const jobId of jobIds) {
    try {
      // Get job status
      const response = UrlFetchApp.fetch(`${API_BASE_URL}/jobs/${jobId}`, {
        headers: {
          'Authorization': token ? `Bearer ${token}` : ''
        },
        muteHttpExceptions: true
      });
      
      if (response.getResponseCode() === 200) {
        const job = JSON.parse(response.getContentText());
        
        // Find row with this job ID
        const row = findRowByJobId(sheet, jobId, config.resultColumn);
        
        if (row > 0) {
          // Update status and URL in result column
          if (job.status === 'pending') {
            sheet.getRange(row, config.resultColumn).setValue('Pending');
          } else if (job.status === 'processing') {
            sheet.getRange(row, config.resultColumn).setValue(`Processing ${job.progress}%`);
          } else if (job.status === 'completed') {
            // Prioritize Google Drive URL if available, otherwise use download URL
            if (job.gdrive_url) {
              sheet.getRange(row, config.resultColumn).setValue(job.gdrive_url);
            } else if (job.output_url) {
              const downloadUrl = `${API_BASE_URL}/jobs/${jobId}/download`;
              sheet.getRange(row, config.resultColumn).setValue(downloadUrl);
            } else {
              sheet.getRange(row, config.resultColumn).setValue('Completed - No URL');
            }
          } else if (job.status === 'failed') {
            sheet.getRange(row, config.resultColumn).setValue('Failed');
            if (job.error) {
              sheet.getRange(row, config.resultColumn).setNote(`Error: ${job.error}`);
            }
          }
        }
        
        // Keep job in active list if still processing
        if (job.status === 'pending' || job.status === 'processing') {
          activeJobs.push(jobId);
        }
      }
    } catch (error) {
      console.error('Error checking job status:', error);
    }
  }
  
  // Update active jobs
  if (activeJobs.length > 0) {
    cache.put('ACTIVE_JOBS', JSON.stringify(activeJobs), 3600);
  } else {
    // All jobs completed, remove trigger
    cache.remove('ACTIVE_JOBS');
    removeTrigger('checkJobStatus');
    
    // Show completion notification
    SpreadsheetApp.getActiveSpreadsheet().toast(
      'All video processing completed',
      'Complete',
      5
    );
  }
}

/**
 * Create progress bar visualization
 */
function createProgressBar(progress) {
  const filled = Math.floor(progress / 10);
  const empty = 10 - filled;
  return '█'.repeat(filled) + '░'.repeat(empty);
}

/**
 * Find row by job ID
 */
function findRowByJobId(sheet, jobId, statusColumn) {
  if (statusColumn <= 0) return -1;
  
  const lastRow = sheet.getLastRow();
  const notes = sheet.getRange(1, statusColumn, lastRow, 1).getNotes();
  
  for (let i = 0; i < notes.length; i++) {
    if (notes[i][0] && notes[i][0].includes(jobId)) {
      return i + 1;
    }
  }
  
  return -1;
}

/**
 * Remove trigger by function name
 */
function removeTrigger(functionName) {
  const triggers = ScriptApp.getProjectTriggers();
  for (const trigger of triggers) {
    if (trigger.getHandlerFunction() === functionName) {
      ScriptApp.deleteTrigger(trigger);
    }
  }
}

/**
 * Get authentication token
 */
function getAuthToken() {
  const userProperties = PropertiesService.getUserProperties();
  return userProperties.getProperty(STORAGE_KEY);
}

/**
 * Set authentication token
 */
function setAuthToken(token) {
  const userProperties = PropertiesService.getUserProperties();
  userProperties.setProperty(STORAGE_KEY, token);
}

/**
 * Test API connection
 */
function testAPIConnection() {
  const ui = SpreadsheetApp.getUi();
  
  try {
    // Test root endpoint
    const response = UrlFetchApp.fetch(API_BASE_URL.replace('/api/v1', ''), {
      muteHttpExceptions: true
    });
    
    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());
      ui.alert('API接続成功', `APIは正常に動作しています。\n\nレスポンス: ${JSON.stringify(data, null, 2)}`, ui.ButtonSet.OK);
    } else {
      ui.alert('API接続エラー', `ステータスコード: ${response.getResponseCode()}\n\nレスポンス: ${response.getContentText()}`, ui.ButtonSet.OK);
    }
  } catch (error) {
    ui.alert('接続エラー', `APIに接続できません。\n\nエラー: ${error.toString()}`, ui.ButtonSet.OK);
  }
}

/**
 * Show settings dialog
 */
function showSettings() {
  const ui = SpreadsheetApp.getUi();
  const config = getColumnConfig();
  
  const html = `
    <div style="padding: 20px;">
      <h3>列の設定</h3>
      <p>現在の設定:</p>
      <ul>
        <li>実行対象列: ${config.targetColumn}</li>
        <li>実行結果列: ${config.resultColumn}</li>
        <li>最初の素材列: ${config.firstMaterialColumn}</li>
      </ul>
      <p>設定を変更するには、スクリプトプロパティを編集してください。</p>
    </div>
  `;
  
  const htmlOutput = HtmlService.createHtmlOutput(html)
    .setWidth(400)
    .setHeight(300);
  
  ui.showModalDialog(htmlOutput, '設定');
}

/**
 * Show help dialog
 */
function showHelp() {
  const ui = SpreadsheetApp.getUi();
  
  const html = `
    <div style="padding: 20px;">
      <h3>使い方</h3>
      <ol>
        <li>スプレッドシートに以下の形式でデータを入力:
          <ul>
            <li>実行対象: ○ (処理する行にマーク)</li>
            <li>素材①: 動画/画像のURL</li>
            <li>使用開始: 開始時間 (例: 0:05 または 5)</li>
            <li>使用秒数: 使用する秒数 (例: 0:10 または 10)</li>
          </ul>
        </li>
        <li>処理したい行を選択</li>
        <li>メニューから「Process Selected Rows」を選択</li>
        <li>処理完了後、実行結果列にダウンロードURLが表示されます</li>
      </ol>
    </div>
  `;
  
  const htmlOutput = HtmlService.createHtmlOutput(html)
    .setWidth(500)
    .setHeight(400);
  
  ui.showModalDialog(htmlOutput, 'ヘルプ');
}

/**
 * Setup column configuration
 */
function setupColumnConfiguration() {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  // 列番号を設定（A=1, B=2, C=3...）
  scriptProperties.setProperty('TARGET_COLUMN', '1');        // A列: 実行対象（○マーク）
  scriptProperties.setProperty('RESULT_COLUMN', '2');        // B列: 実行結果URL
  scriptProperties.setProperty('FIRST_MATERIAL_COLUMN', '3'); // C列: 最初の素材
  scriptProperties.setProperty('STATUS_COLUMN', '2');        // B列: ステータス表示
  
  // 出力設定
  scriptProperties.setProperty('OUTPUT_FORMAT', 'mp4');
  scriptProperties.setProperty('OUTPUT_FPS', '30');
  scriptProperties.setProperty('OUTPUT_CODEC', 'libx264');
  scriptProperties.setProperty('OUTPUT_AUDIO_CODEC', 'aac');
  scriptProperties.setProperty('OUTPUT_QUALITY', 'high');
  
  SpreadsheetApp.getUi().alert('設定完了', '列の設定が完了しました。', SpreadsheetApp.getUi().ButtonSet.OK);
}

/**
 * Debug function to check selected rows
 */
function debugCheckRows() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const selection = sheet.getActiveRange();
  const ui = SpreadsheetApp.getUi();
  
  if (!selection) {
    ui.alert('行を選択してください');
    return;
  }
  
  const startRow = selection.getRow();
  const numRows = selection.getNumRows();
  const config = getColumnConfig();
  
  let debugInfo = `選択範囲: 行 ${startRow} から ${numRows} 行\n\n`;
  debugInfo += `設定された実行対象列: ${config.targetColumn}\n\n`;
  
  for (let i = 0; i < numRows; i++) {
    const row = startRow + i;
    const targetValue = sheet.getRange(row, config.targetColumn).getValue();
    const charCode = targetValue ? targetValue.toString().charCodeAt(0) : 'null';
    
    debugInfo += `行 ${row}: "${targetValue}" (文字コード: ${charCode})\n`;
  }
  
  ui.alert('デバッグ情報', debugInfo, ui.ButtonSet.OK);
}

/**
 * Parse time format (m:ss or seconds)
 * Examples: "0:05" -> 5, "1:30" -> 90, "45" -> 45
 */
function parseTimeFormat(timeValue) {
  if (!timeValue) {
    return 0;
  }
  
  const timeStr = timeValue.toString().trim();
  
  // Check if it contains colon (m:ss format)
  if (timeStr.includes(':')) {
    const parts = timeStr.split(':');
    if (parts.length === 2) {
      const minutes = parseInt(parts[0]) || 0;
      const seconds = parseInt(parts[1]) || 0;
      return minutes * 60 + seconds;
    }
  }
  
  // Otherwise treat as seconds
  return parseFloat(timeStr) || 0;
}

/**
 * Test API connection
 */
function testAPIConnection() {
  const ui = SpreadsheetApp.getUi();
  
  try {
    // Test root endpoint
    const rootResponse = UrlFetchApp.fetch(`${API_BASE_URL.replace('/api/v1', '')}/`, {
      muteHttpExceptions: true
    });
    
    // Test health endpoint
    const healthResponse = UrlFetchApp.fetch(`${API_BASE_URL}/health`, {
      muteHttpExceptions: true
    });
    
    // Test batch endpoint
    const testData = {
      rows: [{
        row_number: 1,
        media_items: [{url: "test.mp4", duration: 5}],
        output_name: "test"
      }]
    };
    
    const batchResponse = UrlFetchApp.fetch(`${API_BASE_URL}/jobs/batch`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      payload: JSON.stringify(testData),
      muteHttpExceptions: true
    });
    
    const results = [
      `Root endpoint: ${rootResponse.getResponseCode()} - ${rootResponse.getContentText()}`,
      `Health endpoint: ${healthResponse.getResponseCode()} - ${healthResponse.getContentText()}`,
      `Batch endpoint: ${batchResponse.getResponseCode()} - ${batchResponse.getContentText()}`
    ].join('\n\n');
    
    ui.alert('API Test Results', results, ui.ButtonSet.OK);
    
  } catch (error) {
    ui.alert('API Test Error', error.toString(), ui.ButtonSet.OK);
  }
}