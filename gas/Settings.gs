/**
 * Show settings dialog
 */
function showSettings() {
  const htmlOutput = HtmlService.createHtmlOutputFromFile('SettingsDialog')
    .setWidth(600)
    .setHeight(700);
  
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'Video Processor Settings');
}

/**
 * Get current settings
 */
function getSettings() {
  const scriptProperties = PropertiesService.getScriptProperties();
  const userProperties = PropertiesService.getUserProperties();
  
  return {
    // API Settings
    apiUrl: scriptProperties.getProperty('API_URL') || API_BASE_URL,
    authToken: userProperties.getProperty(STORAGE_KEY) || '',
    
    // Column Mappings for new format
    targetColumn: parseInt(scriptProperties.getProperty('TARGET_COLUMN') || '1'), // 実行対象
    resultColumn: parseInt(scriptProperties.getProperty('RESULT_COLUMN') || '2'), // 実行結果
    firstMaterialColumn: parseInt(scriptProperties.getProperty('FIRST_MATERIAL_COLUMN') || '3'), // 素材①
    
    // Output Settings
    outputFormat: scriptProperties.getProperty('OUTPUT_FORMAT') || 'mp4',
    outputFps: parseInt(scriptProperties.getProperty('OUTPUT_FPS') || '30'),
    outputResolution: scriptProperties.getProperty('OUTPUT_RESOLUTION') || '',
    outputCodec: scriptProperties.getProperty('OUTPUT_CODEC') || 'libx264',
    outputAudioCodec: scriptProperties.getProperty('OUTPUT_AUDIO_CODEC') || 'aac',
    outputQuality: scriptProperties.getProperty('OUTPUT_QUALITY') || 'high'
  };
}

/**
 * Save settings
 */
function saveSettings(settings) {
  const scriptProperties = PropertiesService.getScriptProperties();
  const userProperties = PropertiesService.getUserProperties();
  
  try {
    // Save API settings
    if (settings.apiUrl) {
      scriptProperties.setProperty('API_URL', settings.apiUrl);
    }
    if (settings.authToken !== undefined) {
      userProperties.setProperty(STORAGE_KEY, settings.authToken);
    }
    
    // Save column mappings for new format
    scriptProperties.setProperty('TARGET_COLUMN', settings.targetColumn.toString());
    scriptProperties.setProperty('RESULT_COLUMN', settings.resultColumn.toString());
    scriptProperties.setProperty('FIRST_MATERIAL_COLUMN', settings.firstMaterialColumn.toString());
    
    // Save output settings
    scriptProperties.setProperty('OUTPUT_FORMAT', settings.outputFormat);
    scriptProperties.setProperty('OUTPUT_FPS', settings.outputFps.toString());
    scriptProperties.setProperty('OUTPUT_RESOLUTION', settings.outputResolution || '');
    scriptProperties.setProperty('OUTPUT_CODEC', settings.outputCodec);
    scriptProperties.setProperty('OUTPUT_AUDIO_CODEC', settings.outputAudioCodec);
    scriptProperties.setProperty('OUTPUT_QUALITY', settings.outputQuality);
    
    return { success: true, message: 'Settings saved successfully!' };
  } catch (error) {
    return { success: false, message: 'Failed to save settings: ' + error.message };
  }
}

/**
 * Test API connection
 */
function testApiConnection() {
  try {
    const settings = getSettings();
    const response = UrlFetchApp.fetch(`${settings.apiUrl}/health`, {
      headers: {
        'Authorization': settings.authToken ? `Bearer ${settings.authToken}` : ''
      },
      muteHttpExceptions: true
    });
    
    if (response.getResponseCode() === 200) {
      return { success: true, message: 'API connection successful!' };
    } else {
      return { success: false, message: 'API returned status: ' + response.getResponseCode() };
    }
  } catch (error) {
    return { success: false, message: 'Connection failed: ' + error.message };
  }
}

/**
 * Show help dialog
 */
function showHelp() {
  const htmlOutput = HtmlService.createHtmlOutputFromFile('HelpDialog')
    .setWidth(700)
    .setHeight(600);
  
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'Video Processor Help');
}

/**
 * Create sample data in spreadsheet
 */
function createSampleData() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const ui = SpreadsheetApp.getUi();
  
  const response = ui.alert(
    'Create Sample Data',
    'This will create sample data in the current sheet. Continue?',
    ui.ButtonSet.YES_NO
  );
  
  if (response !== ui.Button.YES) {
    return;
  }
  
  // Headers for new format
  const headers = [
    '実行対象', '実行結果', 
    '素材①', '使用開始', '使用秒数',
    '素材②', '使用開始', '使用秒数',
    '素材③', '使用開始', '使用秒数'
  ];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]).setFontWeight('bold');
  
  // Sample data
  const sampleData = [
    ['○', '', 'https://example.com/video1.mp4', '0:05', '0:10', 'https://example.com/image1.jpg', '0:00', '0:03', '', '', ''],
    ['○', '', 'https://example.com/video2.mp4', '0:15', '0:20', '', '', '', '', '', ''],
    ['', '', 'https://example.com/video3.mp4', '0:00', '0:05', 'https://example.com/image2.png', '0:00', '0:04', 'https://example.com/video4.mp4', '0:10', '0:08']
  ];
  
  sheet.getRange(2, 1, sampleData.length, sampleData[0].length).setValues(sampleData);
  
  // Auto-resize columns
  sheet.autoResizeColumns(1, headers.length);
  
  ui.alert('Sample data created successfully!');
}