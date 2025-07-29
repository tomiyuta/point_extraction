# point_extraction 本番環境使用ガイド

## 概要
修正版のフィルタリングスクリプトを使用して、FX取引データのCSVファイルを処理します。
日をまたぐ取引の重複判定問題を解決し、正確なフィルタリングを実現します。

## 主な改善点
- ✅ 日付情報を含めた正確な重複判定
- ✅ 日をまたぐ取引の正しい処理
- ✅ 時刻重複の完全除去
- ✅ 本番環境での安定動作

## ファイル構成
```
point_extraction/
├── process_csv_weekly_fixed.py    # 修正版メインスクリプト
├── config.json                    # 設定ファイル
├── run_filtering.sh              # Linux/Mac用実行スクリプト
├── run_filtering.bat             # Windows用実行スクリプト
├── verify_fixed_filtering.py     # 結果検証スクリプト
└── README_PRODUCTION.md          # このファイル
```

## セットアップ

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd point_extraction
```

### 2. データファイルの準備
**重要**: このリポジトリにはデータファイルが含まれていません。以下の手順でデータファイルを準備してください：

#### 必要なデータ形式
CSVファイルには以下の列が必要です：
- `基準日`: 日付（YYYY-MM-DD形式）
- `方向`: Long/Short
- `銘柄`: 通貨ペア（例：EURUSD, USDJPY）
- `エントリー時刻`: 時刻（HH:MM:SS形式）
- `クローズ時刻`: 時刻（HH:MM:SS形式）
- `勝率_30日`: 勝率（XX.XX%形式）
- `合計変動pips_30日`: 数値

#### データファイルの配置
1. データファイルを`point_extraction`フォルダに配置
2. `config.json`の`default_input_file`を実際のファイル名に変更

```json
{
    "win_rate_threshold": 85.0,
    "default_input_file": "your_data_file.csv",
    "output_columns": [...]
}
```

### 3. 仮想環境の作成
```bash
# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy

# Windows
python -m venv venv
venv\Scripts\activate.bat
pip install pandas numpy
```

### 4. 設定ファイルの確認
`config.json`の内容を確認し、必要に応じて調整：
```json
{
    "win_rate_threshold": 85.0,
    "default_input_file": "your_data_file.csv",
    "output_columns": [
        "方向", "銘柄", "エントリー時刻", "クローズ時刻", 
        "勝率_30日", "合計変動pips_30日"
    ]
}
```

## 使用方法

### 基本的な実行（推奨）

#### Linux/Mac
```bash
# 設定ファイルの値を使用
./run_filtering.sh

# ファイル名を指定
./run_filtering.sh input_data.csv

# 出力ファイル名も指定
./run_filtering.sh input_data.csv output_result.csv

# 勝率閾値も指定
./run_filtering.sh input_data.csv output_result.csv 90.0
```

#### Windows
```cmd
# 設定ファイルの値を使用
run_filtering.bat

# ファイル名を指定
run_filtering.bat input_data.csv

# 出力ファイル名も指定
run_filtering.bat input_data.csv output_result.csv

# 勝率閾値も指定
run_filtering.bat input_data.csv output_result.csv 90.0
```

### 直接実行
```bash
# 仮想環境をアクティベート
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate.bat  # Windows

# スクリプト実行
python3 process_csv_weekly_fixed.py
```

## 出力ファイル

### ファイル名
- 自動生成: `filtered_result_YYYYMMDD.csv`
- 手動指定: 指定したファイル名

### 出力形式
```csv
方向,銘柄,エントリー時刻,クローズ時刻,勝率_30日,合計変動pips_30日
Long,EURUSD,0:07:00,0:28:00,86.36%,170.5
Short,EURUSD,1:13:00,1:37:00,90.91%,101.5
...
```

## 処理内容

### 1. 勝率フィルタ
- 指定された閾値（デフォルト85.0%）以上の勝率の取引のみ抽出

### 2. 時刻重複除去（修正版）
- 日付情報を含めた正確な重複判定
- 日をまたぐ取引を正しく処理
- 重複がある場合、勝率が高い方を残す
- 勝率が同じ場合は合計変動pipsが大きい方を残す

### 3. データ整理
- エントリー時刻の早い順にソート
- 必要な6列のみを出力

## 結果検証

処理結果を検証するには：
```bash
python3 verify_fixed_filtering.py
```

検証項目：
- ✅ 勝率フィルタの正確性
- ✅ 時刻重複の完全除去
- ✅ 列の形式確認
- ✅ データ統計情報
- ✅ 時刻順ソート確認

## トラブルシューティング

### よくある問題

#### 1. データファイルが見つからない
```bash
# ファイル名とパスを確認
ls -la *.csv

# config.jsonの設定を確認
cat config.json
```

#### 2. 仮想環境が見つからない
```bash
# 仮想環境を再作成
python3 -m venv venv
source venv/bin/activate
pip install pandas numpy
```

#### 3. ライブラリがインストールされていない
```bash
pip install pandas numpy
```

#### 4. 権限エラー（Linux/Mac）
```bash
chmod +x run_filtering.sh
```

### ログ確認
実行時に詳細なログが出力されます：
- 処理開始・終了時刻
- 各段階での行数
- エラー情報

## パフォーマンス

### 処理時間の目安
- 10,000行のデータ: 約10-30秒
- 100,000行のデータ: 約1-3分

### メモリ使用量
- 通常の処理: 100MB以下
- 大規模データ: 500MB以下

## 更新履歴

### v2.0 (修正版)
- 日付情報を含めた重複判定を実装
- 日をまたぐ取引の正しい処理
- 時刻重複の完全除去を実現
- 本番環境での安定動作を確認

### v1.0 (元版)
- 基本的なフィルタリング機能
- 時刻重複判定に問題あり

## サポート

問題が発生した場合は：
1. ログを確認
2. `verify_fixed_filtering.py`で結果を検証
3. 設定ファイルの内容を確認
4. 必要に応じて開発者に連絡 