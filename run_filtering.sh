#!/bin/bash

# point_extraction フィルタリング実行スクリプト（修正版）
# 使用方法: ./run_filtering.sh [入力ファイル] [出力ファイル] [勝率閾値]

echo "=== point_extraction フィルタリング開始 ==="
echo "日時: $(date)"

# 仮想環境の確認とアクティベート
if [ ! -d "venv" ]; then
    echo "仮想環境が見つかりません。作成中..."
    python3 -m venv venv
fi

echo "仮想環境をアクティベート中..."
source venv/bin/activate

# 必要なライブラリの確認とインストール
echo "必要なライブラリを確認中..."
pip install pandas numpy

# 引数の処理
INPUT_FILE=${1:-""}
OUTPUT_FILE=${2:-""}
WIN_RATE=${3:-""}

echo "=== 実行パラメータ ==="
echo "入力ファイル: ${INPUT_FILE:-'設定ファイルから自動取得'}"
echo "出力ファイル: ${OUTPUT_FILE:-'自動生成'}"
echo "勝率閾値: ${WIN_RATE:-'設定ファイルから自動取得'}%"

# 修正版スクリプトの実行
echo ""
echo "=== フィルタリング処理開始 ==="

if [ -n "$INPUT_FILE" ] && [ -n "$OUTPUT_FILE" ] && [ -n "$WIN_RATE" ]; then
    # 全パラメータ指定
    python3 process_csv_weekly_fixed.py "$INPUT_FILE" "$OUTPUT_FILE" "$WIN_RATE"
elif [ -n "$INPUT_FILE" ] && [ -n "$OUTPUT_FILE" ]; then
    # 入力ファイルと出力ファイル指定
    python3 process_csv_weekly_fixed.py "$INPUT_FILE" "$OUTPUT_FILE"
elif [ -n "$INPUT_FILE" ]; then
    # 入力ファイルのみ指定
    python3 process_csv_weekly_fixed.py "$INPUT_FILE"
else
    # 設定ファイルから自動取得
    python3 process_csv_weekly_fixed.py
fi

# 実行結果の確認
if [ $? -eq 0 ]; then
    echo ""
    echo "=== 処理完了 ==="
    echo "日時: $(date)"
    
    # 最新の出力ファイルを確認
    LATEST_FILE=$(ls -t filtered_result_*.csv 2>/dev/null | head -1)
    if [ -n "$LATEST_FILE" ]; then
        echo "最新の出力ファイル: $LATEST_FILE"
        echo "ファイルサイズ: $(ls -lh "$LATEST_FILE" | awk '{print $5}')"
        echo "行数: $(wc -l < "$LATEST_FILE")"
    fi
else
    echo ""
    echo "=== エラーが発生しました ==="
    exit 1
fi 