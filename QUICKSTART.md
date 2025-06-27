# 🚀 クイックスタートガイド

## 必要な環境
- Docker & Docker Compose (推奨)
- または Python 3.8+, Redis, FFmpeg

## 1. バックエンドを起動

### Docker使用（推奨）
```bash
cd spreadsheet-video-processor
docker-compose up -d
```

### 手動セットアップ
```bash
./setup.sh
```

## 2. Google Apps Script を設定

### 2.1 新しいスプレッドシートを作成
1. [Google Sheets](https://sheets.google.com) を開く
2. 新しいスプレッドシートを作成

### 2.2 Apps Script を追加
1. `拡張機能` → `Apps Script`
2. `gas/` フォルダの全ファイルをコピー：
   - `Code.gs`
   - `Settings.gs`
   - `SettingsDialog.html`
   - `ProcessingDialog.html`
   - `HelpDialog.html`

### 2.3 API URL を設定
1. スプレッドシートに戻る
2. `Video Processor` → `Settings`
3. API URL: `http://localhost:8000/api/v1` (ローカル環境の場合)
4. 保存

## 3. テスト実行

### 3.1 サンプルデータを作成
1. `Video Processor` → `Help` → `Create Sample Data`

### 3.2 実際のデータで試す
| Media URLs | Duration (seconds) | Status | Result URL |
|------------|-------------------|---------|------------|
| https://example.com/video1.mp4 | 5 | | |
| https://example.com/image1.jpg,https://example.com/video2.mp4 | 3,7 | | |

### 3.3 処理実行
1. 処理したい行を選択
2. `Video Processor` → `Process Selected Rows`
3. Status列で進捗確認
4. 完了後、Result URL列からダウンロード

## 4. 本格運用（オプション）

### 4.1 クラウドデプロイ
- Heroku, Railway, DigitalOcean などにデプロイ
- 環境変数でAPI URLを設定

### 4.2 認証設定（オプション）
```bash
# Google OAuth設定
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 4.3 ストレージ設定
```bash
# S3使用の場合
STORAGE_BACKEND=s3
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=your-bucket
```

## トラブルシューティング

### API接続エラー
- バックエンドが起動しているか確認
- API URLが正しいか確認
- ファイアウォール設定確認

### 処理が失敗する
- メディアファイルがアクセス可能か確認
- ファイル形式が対応しているか確認
- ログ確認: `docker-compose logs worker`

### よくある質問
**Q: どのファイル形式に対応していますか？**
A: 動画（MP4, MOV, AVI等）、画像（JPG, PNG等）

**Q: 複数ファイルはどう指定しますか？**
A: カンマ区切りで指定（例: video1.mp4,image1.jpg）

**Q: 処理時間はどのくらいかかりますか？**
A: ファイルサイズと品質設定により変動（通常数分）