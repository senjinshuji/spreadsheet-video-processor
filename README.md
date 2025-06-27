# Spreadsheet Video Processor

Google スプレッドシートから直接動画・画像を結合処理できるシステム

## 概要

このシステムは以下の3つのコンポーネントで構成されています：

1. **Backend API** - FastAPIベースの動画処理API
2. **Google Apps Script** - スプレッドシートのメニュー統合
3. **Celery Worker** - バックグラウンド動画処理

## 主な機能

- 📊 **スプレッドシート統合** - Google スプレッドシートにカスタムメニューを追加
- 🎯 **範囲選択** - 複数行を選択して一括処理
- 🎬 **動画・画像結合** - 複数のメディアファイルを1つの動画に結合
- ⏱️ **トリミング** - 各メディアを指定秒数にトリミング
- 📈 **進捗表示** - リアルタイムで処理状況を確認
- 💾 **自動ダウンロード** - 処理完了後、スプレッドシートにダウンロードリンクを追加

## システム構成

```
spreadsheet-video-processor/
├── backend/               # FastAPI バックエンドAPI
│   ├── main.py           # APIエンドポイント
│   ├── celery_app.py     # Celery ワーカー
│   ├── video_processor.py # 動画処理ロジック
│   └── storage.py        # ファイルストレージ管理
├── gas/                  # Google Apps Script
│   ├── Code.gs          # メインスクリプト
│   ├── Settings.gs      # 設定管理
│   └── *.html           # UIダイアログ
└── docker-compose.yml    # Docker構成
```

## セットアップ

### 1. バックエンドのセットアップ

```bash
# リポジトリをクローン
git clone <repository-url>
cd spreadsheet-video-processor

# Dockerで起動
docker-compose up -d

# または、ローカルでセットアップ
cd backend
pip install -r requirements.txt

# Redis を起動 (別ターミナル)
redis-server

# API を起動
python main.py

# Celery ワーカーを起動 (別ターミナル)
celery -A celery_app worker --loglevel=info
```

### 2. Google Apps Script のセットアップ

1. Google スプレッドシートを開く
2. 拡張機能 → Apps Script
3. `gas/` フォルダ内の全ファイルをコピー
4. プロジェクトを保存
5. スプレッドシートをリロード

### 3. API URLの設定

1. スプレッドシートで「Video Processor → Settings」
2. API URLを入力（例: `https://your-api-domain.com/api/v1`）
3. 保存

## 使い方

### スプレッドシートの準備

| Media URLs | Duration (seconds) | Status | Download Link |
|------------|-------------------|---------|---------------|
| video1.mp4,image1.jpg | 5,3 | | |
| video2.mp4 | 10 | | |

### 処理の実行

1. 処理したい行を選択
2. メニューから「Video Processor → Process Selected Rows」
3. 確認ダイアログで「Yes」
4. 処理状況は Status 列で確認
5. 完了後、Download Link 列からダウンロード

## 高度な設定

### 列のカスタマイズ

Settings で各列の位置を変更可能：
- URL Column: メディアファイルのURL
- Duration Column: 秒数
- Start Time Column: トリミング開始位置（オプション）
- Output Name Column: 出力ファイル名（オプション）

### 出力設定

- **Format**: MP4, AVI, MOV, WebM
- **FPS**: 1-120
- **Resolution**: 1920x1080, 1280x720 など
- **Quality**: Low, Medium, High

## API エンドポイント

- `POST /api/v1/jobs/create` - 単一ジョブ作成
- `POST /api/v1/jobs/batch` - バッチジョブ作成
- `GET /api/v1/jobs/{job_id}` - ジョブステータス確認
- `GET /api/v1/jobs/{job_id}/download` - 結果ダウンロード

## 環境変数

```env
# API設定
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# ストレージ設定
STORAGE_BACKEND=local  # local, s3, minio
STORAGE_PATH=./storage

# S3/MinIO設定（オプション）
S3_ENDPOINT=https://s3.amazonaws.com
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET=video-processor

# Celery設定
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## トラブルシューティング

### 処理が開始されない
- API URLが正しいか確認
- Celery ワーカーが起動しているか確認
- Redis が起動しているか確認

### 処理が失敗する
- メディアファイルのURLがアクセス可能か確認
- ファイル形式がサポートされているか確認
- ログを確認: `docker-compose logs worker`

## ライセンス

MIT License