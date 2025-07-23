import pandas as pd
import numpy as np
from datetime import datetime, time
import sys
import os
import json

def load_config():
    """設定ファイルを読み込み"""
    config_file = 'config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        # デフォルト設定
        return {
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

def parse_time(time_str):
    """時刻文字列をtimeオブジェクトに変換"""
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except:
        return None

def time_overlap(start1, end1, start2, end2):
    """2つの時間帯が重複するかチェック"""
    if start1 <= end2 and start2 <= end1:
        return True
    return False

def process_csv(input_file=None, output_file=None, win_rate_threshold=None):
    """
    CSVファイルを処理する関数
    
    Args:
        input_file (str): 入力CSVファイル名
        output_file (str): 出力CSVファイル名（Noneの場合は自動生成）
        win_rate_threshold (float): 勝率の閾値（Noneの場合は設定ファイルから読み込み）
    """
    
    # 設定ファイルを読み込み
    config = load_config()
    
    # パラメータの設定
    if input_file is None:
        input_file = config.get('default_input_file', '20250720.csv')
    
    if win_rate_threshold is None:
        win_rate_threshold = config.get('win_rate_threshold', 85.0)
    
    # 出力ファイル名が指定されていない場合は自動生成
    if output_file is None:
        today = datetime.now().strftime('%Y%m%d')
        output_file = f'filtered_result_{today}.csv'
    
    # CSVファイルを読み込み
    if not os.path.exists(input_file):
        print(f"エラー: ファイル '{input_file}' が見つかりません。")
        return
    
    print(f"=== CSV処理開始 ===")
    print(f"入力ファイル: {input_file}")
    print(f"勝率閾値: {win_rate_threshold}%")
    
    df = pd.read_csv(input_file)
    
    print(f"元のデータ行数: {len(df)}")
    
    # 1. 勝率_30日が指定された閾値以上の行のみ抽出
    # 勝率の列から%を除去して数値に変換
    df['勝率_30日_数値'] = df['勝率_30日'].str.replace('%', '').astype(float)
    filtered_df = df[df['勝率_30日_数値'] >= win_rate_threshold].copy()
    
    print(f"勝率{win_rate_threshold}%以上フィルタ後: {len(filtered_df)}行")
    
    # 2. エントリー時刻とクローズ時刻をtimeオブジェクトに変換
    filtered_df['エントリー時刻_時間'] = filtered_df['エントリー時刻'].apply(parse_time)
    filtered_df['クローズ時刻_時間'] = filtered_df['クローズ時刻'].apply(parse_time)
    
    # 時刻が解析できない行を除外
    filtered_df = filtered_df.dropna(subset=['エントリー時刻_時間', 'クローズ時刻_時間'])
    print(f"時刻解析後: {len(filtered_df)}行")
    
    # 3. 時刻重複をチェックして重複する行の組み合わせを特定
    indices_to_remove = set()
    
    for i in range(len(filtered_df)):
        if i in indices_to_remove:
            continue
            
        for j in range(i + 1, len(filtered_df)):
            if j in indices_to_remove:
                continue
                
            # 時刻重複をチェック
            if time_overlap(
                filtered_df.iloc[i]['エントリー時刻_時間'],
                filtered_df.iloc[i]['クローズ時刻_時間'],
                filtered_df.iloc[j]['エントリー時刻_時間'],
                filtered_df.iloc[j]['クローズ時刻_時間']
            ):
                # 勝率を比較
                win_rate_i = filtered_df.iloc[i]['勝率_30日_数値']
                win_rate_j = filtered_df.iloc[j]['勝率_30日_数値']
                
                # 勝率が高い方を残す
                if win_rate_i > win_rate_j:
                    indices_to_remove.add(j)
                elif win_rate_i < win_rate_j:
                    indices_to_remove.add(i)
                else:
                    # 勝率が同じ場合は合計変動pips_30日が大きい方を残す
                    pips_i = filtered_df.iloc[i]['合計変動pips_30日']
                    pips_j = filtered_df.iloc[j]['合計変動pips_30日']
                    
                    if pips_i < pips_j:
                        indices_to_remove.add(i)
                    else:
                        indices_to_remove.add(j)
    
    # 重複する行を削除
    final_df = filtered_df.drop(filtered_df.index[list(indices_to_remove)])
    print(f"重複除去後: {len(final_df)}行")
    
    # 4. エントリー時刻でソート
    final_df = final_df.sort_values('エントリー時刻_時間')
    
    # 5. 必要な列のみを選択
    output_columns = config.get('output_columns', [
        "方向",
        "銘柄", 
        "エントリー時刻",
        "クローズ時刻",
        "勝率_30日",
        "合計変動pips_30日"
    ])
    
    # 出力用のDataFrameを作成
    result_df = final_df[output_columns].copy()
    
    # 結果を保存
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\n=== 処理結果 ===")
    print(f"最終行数: {len(result_df)}")
    print(f"出力ファイル: {output_file}")
    
    # 最初の10行を表示
    print(f"\n=== 最初の10行 ===")
    for idx, row in result_df.head(10).iterrows():
        print(f"時刻: {row['エントリー時刻']}-{row['クローズ時刻']}, "
              f"銘柄: {row['銘柄']}, 方向: {row['方向']}, "
              f"勝率30日: {row['勝率_30日']}, 合計変動pips: {row['合計変動pips_30日']}")

if __name__ == "__main__":
    # コマンドライン引数の処理
    input_file = None
    output_file = None
    win_rate_threshold = None
    
    if len(sys.argv) >= 2:
        input_file = sys.argv[1]
    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    if len(sys.argv) >= 4:
        win_rate_threshold = float(sys.argv[3])
    
    process_csv(input_file, output_file, win_rate_threshold) 