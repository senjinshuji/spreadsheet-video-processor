// 列設定用のセットアップ関数
// Apps Scriptエディタでこの関数を実行してください

function setupColumnConfiguration() {
  const scriptProperties = PropertiesService.getScriptProperties();
  
  // スプレッドシートの列番号を設定
  // A列 = 1, B列 = 2, C列 = 3...
  
  scriptProperties.setProperty('TARGET_COLUMN', '1');        // A列: 実行対象（○マーク）
  scriptProperties.setProperty('RESULT_COLUMN', '2');        // B列: 実行結果（URL記載）
  scriptProperties.setProperty('FIRST_MATERIAL_COLUMN', '3'); // C列: 素材①
  scriptProperties.setProperty('STATUS_COLUMN', '2');        // B列: ステータス表示（実行結果と同じ）
  
  // 出力設定
  scriptProperties.setProperty('OUTPUT_FORMAT', 'mp4');
  scriptProperties.setProperty('OUTPUT_FPS', '30');
  scriptProperties.setProperty('OUTPUT_CODEC', 'libx264');
  scriptProperties.setProperty('OUTPUT_AUDIO_CODEC', 'aac');
  scriptProperties.setProperty('OUTPUT_QUALITY', 'high');
  
  console.log('設定が完了しました！');
  
  // 確認用に現在の設定を表示
  const properties = scriptProperties.getProperties();
  console.log('現在の設定:');
  for (const key in properties) {
    console.log(`${key}: ${properties[key]}`);
  }
}

// 現在の設定を確認する関数
function checkCurrentSettings() {
  const scriptProperties = PropertiesService.getScriptProperties();
  const properties = scriptProperties.getProperties();
  
  console.log('=== 現在の列設定 ===');
  console.log('実行対象列（TARGET_COLUMN）: ' + (properties.TARGET_COLUMN || '未設定'));
  console.log('実行結果列（RESULT_COLUMN）: ' + (properties.RESULT_COLUMN || '未設定'));
  console.log('最初の素材列（FIRST_MATERIAL_COLUMN）: ' + (properties.FIRST_MATERIAL_COLUMN || '未設定'));
  console.log('ステータス列（STATUS_COLUMN）: ' + (properties.STATUS_COLUMN || '未設定'));
  
  return properties;
}