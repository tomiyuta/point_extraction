# Google Drive上でPythonコードを実行する方法

## 方法1: Google Colab（推奨）

### 手順1: Google Colabにアクセス
1. [Google Colab](https://colab.research.google.com/) にアクセス
2. Googleアカウントでログイン

### 手順2: 新しいノートブックを作成
1. 「ファイル」→「新しいノートブック」をクリック
2. または、`process_csv_weekly_colab.ipynb`ファイルをGoogle Driveにアップロードして開く

### 手順3: Google Driveをマウント
```python
from google.colab import drive
drive.mount('/content/drive')
```
- 認証画面が表示されるので、指示に従って認証

### 手順4: ファイルをGoogle Driveにアップロード
1. Google Driveの「マイドライブ」に「ポイント抽出」フォルダを作成
2. 以下のファイルをアップロード：
   - `20250720.csv`
   - `config.json`
   - `process_csv_weekly_colab.ipynb`

### 手順5: コードを実行
1. 各セルを順番に実行（Shift + Enter）
2. 最後のセルで処理が実行される

### 手順6: 結果の確認
- 処理結果はGoogle Driveの「ポイント抽出」フォルダに保存される
- ファイル名: `filtered_result_YYYYMMDD.csv`

## 方法2: Google Apps Script

### 手順1: Google Apps Scriptにアクセス
1. [Google Apps Script](https://script.google.com/) にアクセス
2. Googleアカウントでログイン

### 手順2: 新しいプロジェクトを作成
1. 「新しいプロジェクト」をクリック
2. プロジェクト名を「CSV処理」などに変更

### 手順3: コードを貼り付け
1. `google_apps_script.js`の内容をコピー
2. エディタに貼り付け

### 手順4: 実行
1. 「実行」ボタンをクリック
2. 初回実行時は権限の承認が必要

### 手順5: 結果の確認
- 処理結果はGoogle Driveのルートに保存される

## 方法3: Google Cloud Functions（上級者向け）

### 手順1: Google Cloud Consoleにアクセス
1. [Google Cloud Console](https://console.cloud.google.com/) にアクセス
2. プロジェクトを作成または選択

### 手順2: Cloud Functionsを有効化
1. Cloud Functions APIを有効化
2. 新しい関数を作成

### 手順3: コードをデプロイ
```python
import pandas as pd
import numpy as np
from datetime import datetime, time
import json
from google.cloud import storage

def process_csv_cloud_function(request):
    # 元のprocess_csv関数のコードをここに配置
    # Google Cloud Storageからファイルを読み込み
    # 結果をGoogle Cloud Storageに保存
    pass
```

## 注意事項

### ファイルパス
- Google Colab: `/content/drive/MyDrive/ポイント抽出/`
- Google Apps Script: Google Driveのルート
- ファイル名は正確に指定する必要があります

### 権限
- Google Driveへのアクセス権限が必要
- 初回実行時は認証が必要

### データサイズ
- 大きなCSVファイルの場合、処理時間がかかる可能性があります
- Google Colabの場合はセッション時間制限に注意

### エラー対処
- ファイルが見つからない場合：パスとファイル名を確認
- 権限エラー：Google Driveの共有設定を確認
- メモリエラー：データサイズを確認

## 推奨方法

**Google Colab**を推奨します：
- 無料で使用可能
- Python環境が整っている
- インタラクティブな実行が可能
- 結果の可視化が簡単
- コードの修正が容易

## トラブルシューティング

### よくある問題と解決方法

1. **ファイルが見つからない**
   - ファイル名の確認
   - パスの確認
   - ファイルのアップロード確認

2. **権限エラー**
   - Google Driveの共有設定確認
   - アカウントの認証確認

3. **メモリ不足**
   - データサイズの確認
   - バッチ処理の検討

4. **文字化け**
   - エンコーディング設定の確認
   - UTF-8での保存確認 