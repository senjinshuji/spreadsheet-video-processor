# 動作する動画URL例

## 確認済み - 動作するURL

### 直接アクセス可能な動画ファイル
```
# 小さなサンプル動画（推奨）
https://file-examples.com/storage/fe68c1b7317bb42832fcd86/2017/10/file_example_MP4_480_1_5MG.mp4

# 短い動画（5秒）
https://sample-videos.com/zip/10/mp4/SampleVideo_360x240_1mb.mp4

# テスト用動画
https://www.w3schools.com/html/mov_bbb.mp4
```

## スプレッドシートでの推奨フォーマット

### 実行対象 | 実行結果 | 素材① | 使用開始 | 使用秒数 | 素材② | 使用開始 | 使用秒数
```
○ | [結果URL] | https://file-examples.com/storage/fe68c1b7317bb42832fcd86/2017/10/file_example_MP4_480_1_5MG.mp4 | 0 | 3 | https://www.w3schools.com/html/mov_bbb.mp4 | 0 | 2
```

## 注意事項

1. **直接リンク可能なファイル**のみ使用
2. **HTTPSを推奨**（セキュリティ上）
3. **ファイルサイズは10MB以下を推奨**（処理時間短縮）
4. **MP4形式を推奨**（最も互換性が高い）

## 動作確認方法

動画URLが正しく動作するかチェック:
```bash
curl -I [URL]
```

Content-Typeが`video/mp4`や`video/*`であることを確認。