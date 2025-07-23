# CSV処理スクリプト

## 概要
FX取引データのCSVファイルを処理して、高勝率で時刻重複のない取引データを抽出します。

## 処理内容
1. **勝率フィルタ**: 勝率_30日が指定された閾値以上の行のみ抽出
2. **時刻重複除去**: エントリー・クローズ時刻が重複する行を検出し、合計変動pips_30日が大きいものを残す
3. **時刻順ソート**: エントリー時刻の早い順に並び替え
4. **列抽出**: 必要な6列のみを出力

## 出力列
- 方向
- 銘柄
- エントリー時刻
- クローズ時刻
- 勝率_30日
- 合計変動pips_30日

## 設定ファイル (config.json)
```json
{
    "win_rate_threshold": 85.0,
    "default_input_file": "20250720.csv",
    "output_columns": [
        "方向",
        "銘柄", 
        "エントリー時刻",
        "クローズ時刻",
        "勝率_30日",
        "合計変動pips_30日"
    ]
}
```

### 設定項目
- `win_rate_threshold`: 勝率の閾値（デフォルト: 85.0%）
- `default_input_file`: デフォルトの入力ファイル名
- `output_columns`: 出力する列名のリスト

## 使用方法

### 基本的な使用（設定ファイルの値を使用）
```bash
python3 process_csv_weekly.py
```

### ファイル名を指定
```bash
python3 process_csv_weekly.py 入力ファイル名.csv
```

### 出力ファイル名も指定
```bash
python3 process_csv_weekly.py 入力ファイル名.csv 出力ファイル名.csv
```

### 勝率閾値も指定
```bash
python3 process_csv_weekly.py 入力ファイル名.csv 出力ファイル名.csv 90.0
```

## 必要なライブラリ
```bash
pip3 install pandas numpy
```

## ファイル構成
- `process_csv_weekly.py` - メインスクリプト
- `config.json` - 設定ファイル
- `20250720.csv` - 元データ
- `final_result.csv` - 処理結果 