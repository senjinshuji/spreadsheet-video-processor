# Google Drive連携の設定方法

このガイドでは、処理した動画を自動的にGoogle Driveにアップロードし、結果をスプレッドシートに設定する方法を説明します。

## 1. Google Cloud Platform (GCP) でのサービスアカウント作成

### 1.1 プロジェクト作成またはアクセス
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. 新しいプロジェクトを作成するか、既存のプロジェクトを選択

### 1.2 Google Drive API の有効化
1. 「API とサービス」→「ライブラリ」に移動
2. "Google Drive API" を検索して選択
3. 「有効にする」をクリック

### 1.3 サービスアカウントの作成
1. 「API とサービス」→「認証情報」に移動
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名: `video-processor-drive`
4. 説明: `Video processor Google Drive upload service`
5. 「作成」をクリック

### 1.4 キーファイルのダウンロード
1. 作成されたサービスアカウントをクリック
2. 「キー」タブに移動
3. 「鍵を追加」→「新しい鍵を作成」
4. 「JSON」を選択してダウンロード
5. ファイル名を `google-drive-credentials.json` に変更

## 2. Google Drive フォルダの設定

### 2.1 専用フォルダの作成
1. Google Drive で新しいフォルダを作成（例：「Video Processor Results」）
2. フォルダを右クリック→「共有」
3. サービスアカウントのメールアドレスを追加（編集者権限）
4. フォルダのURLからフォルダIDを取得
   - URL例: `https://drive.google.com/drive/folders/1ABC123DEF456GHI789`
   - フォルダID: `1ABC123DEF456GHI789`

## 3. 環境変数の設定

バックエンドサーバーで以下の環境変数を設定：

```bash
# Google Drive 認証情報ファイルのパス
export GOOGLE_DRIVE_CREDENTIALS="/path/to/google-drive-credentials.json"

# アップロード先フォルダID
export GOOGLE_DRIVE_FOLDER_ID="1ABC123DEF456GHI789"
```

### Docker使用の場合
```yaml
# docker-compose.yml に追加
environment:
  - GOOGLE_DRIVE_CREDENTIALS=/app/credentials/google-drive-credentials.json
  - GOOGLE_DRIVE_FOLDER_ID=1ABC123DEF456GHI789
volumes:
  - ./google-drive-credentials.json:/app/credentials/google-drive-credentials.json:ro
```

## 4. 動作確認

### 4.1 認証情報の確認
サーバーログで以下を確認：
```
INFO - Google Drive authentication successful
```

### 4.2 テスト実行
スプレッドシートで動画処理を実行して：
1. 「Processing...」→「Processing 100%」→「Google Drive URL」の流れを確認
2. 結果列にGoogle DriveのURLが設定されることを確認
3. URLをクリックして動画が再生できることを確認

## 5. トラブルシューティング

### 認証エラーの場合
- サービスアカウントのJSONファイルが正しい場所にあるか確認
- ファイルの権限を確認（読み取り可能）
- JSON形式が正しいか確認

### アップロードエラーの場合
- フォルダIDが正しいか確認
- サービスアカウントがフォルダにアクセス権を持っているか確認
- Google Drive APIが有効になっているか確認

### ログの確認
```bash
# サーバーのログを確認
docker logs your-container-name | grep -i "drive"
```

## 6. セキュリティ注意事項

- サービスアカウントのJSONファイルは秘密情報です
- Gitリポジトリにコミットしないでください
- 本番環境では適切な権限管理を行ってください
- 定期的にサービスアカウントキーを更新してください