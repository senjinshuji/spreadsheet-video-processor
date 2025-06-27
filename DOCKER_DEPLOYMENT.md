# RenderでDockerを使用したデプロイ手順

## 手順1: Dockerfileの準備

既にDockerfileは用意されています（`backend/Dockerfile`）:
- Python 3.11を使用
- FFmpegとImageMagickをインストール
- MoviePyを含む全ての依存関係をインストール

## 手順2: render.yamlの更新

```yaml
services:
  - type: web
    name: video-processor-docker
    env: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    envVars:
      - key: PORT
        value: 10000
      - key: STORAGE_PATH
        value: /tmp/videos
```

## 手順3: main.pyを元に戻す

```bash
cd backend
cp main_with_moviepy.py main.py
```

## 手順4: 新しいサービスの作成

1. Renderダッシュボードで「New +」→「Web Service」
2. GitHubリポジトリを接続
3. 以下の設定を使用：
   - **Name**: video-processor-docker
   - **Environment**: Docker
   - **Dockerfile Path**: ./backend/Dockerfile
   - **Docker Build Context Directory**: ./backend
   - **Plan**: Free

## 手順5: 環境変数の設定

Renderダッシュボードで以下を設定：
- `PORT`: 10000
- `STORAGE_PATH`: /tmp/videos

## 手順6: デプロイ

1. 「Create Web Service」をクリック
2. ビルドが完了するまで待つ（5-10分）
3. 新しいURLが発行される

## 手順7: Google Apps Scriptの更新

新しいサービスURLで`Code.gs`を更新：
```javascript
const API_BASE_URL = 'https://video-processor-docker.onrender.com/api/v1';
```

## メリット

- ✅ FFmpegが正しくインストールされる
- ✅ MoviePyが動作する
- ✅ 実際の動画処理が可能
- ✅ システム依存関係の問題を回避

## デメリット

- ⚠️ 新しいURLになる
- ⚠️ ビルド時間が長い（5-10分）
- ⚠️ 無料プランではメモリ制限あり

## 注意事項

1. **無料プランの制限**
   - メモリ: 512MB
   - 月750時間まで
   - 14日間アクティビティがないとスリープ

2. **大きな動画の処理**
   - メモリ制限により失敗する可能性
   - 10秒以下の短い動画でテスト推奨

3. **ストレージ**
   - `/tmp`は一時的
   - 処理後のファイルは消える可能性