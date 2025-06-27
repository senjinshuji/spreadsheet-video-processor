# 実際の動画処理を有効にする方法

現在はモック実装で動作していますが、実際の動画処理を有効にする手順です。

## 方法1: Dockerを使用（推奨）

1. **Renderでサービスタイプを変更**
   - ダッシュボードでサービスを選択
   - Settings → Change Service Type
   - "Docker" を選択

2. **環境変数を設定**
   - `DOCKER_BUILD_CONTEXT_DIR`: backend
   - `PORT`: 10000

3. **main.pyを元に戻す**
   ```bash
   cd backend
   cp main_with_moviepy.py main.py
   git add main.py
   git commit -m "Enable MoviePy for video processing"
   git push
   ```

## 方法2: ビルドスクリプトを使用

1. **build.shを作成**
   ```bash
   #!/bin/bash
   apt-get update
   apt-get install -y ffmpeg
   pip install -r requirements.txt
   ```

2. **render.yamlを更新**
   ```yaml
   buildCommand: |
     cd backend
     chmod +x build.sh
     ./build.sh
   ```

## 方法3: 軽量な動画処理ライブラリを使用

MoviePyの代わりに、より軽量なライブラリを使用：
- ffmpeg-python
- opencv-python

## 現在の制限事項

Renderの無料プランでは：
- メモリ: 512MB
- CPU: 0.1
- ストレージ: 一時的

大きな動画ファイルの処理には制限があります。

## 推奨事項

1. **小さな動画でテスト**: 10秒以下、低解像度
2. **S3などの外部ストレージ**: 処理済みファイルの保存
3. **非同期処理**: Celeryなどのタスクキューを使用