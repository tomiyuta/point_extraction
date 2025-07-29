import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime, time, timedelta

def parse_datetime_with_date(date_str, entry_time_str, close_time_str):
    """日付と時刻を組み合わせてdatetimeオブジェクトに変換"""
    try:
        # 基準日を日付として使用
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        entry_time_obj = datetime.strptime(entry_time_str, '%H:%M:%S').time()
        close_time_obj = datetime.strptime(close_time_str, '%H:%M:%S').time()
        
        # 日付と時刻を組み合わせ
        entry_datetime = datetime.combine(date_obj, entry_time_obj)
        close_datetime = datetime.combine(date_obj, close_time_obj)
        
        # クローズ時刻がエントリー時刻より早い場合は翌日として扱う
        if close_datetime < entry_datetime:
            close_datetime += timedelta(days=1)
            
        return entry_datetime, close_datetime
    except:
        return None, None

def time_overlap_with_date(entry1, close1, entry2, close2):
    """日付情報を含めた2つの時間帯が重複するかチェック"""
    if entry1 is None or close1 is None or entry2 is None or close2 is None:
        return False
    
    # 日付情報を含めた重複判定
    if entry1 <= close2 and entry2 <= close1:
        return True
    return False

def verify_fixed_filtering():
    """修正版フィルタリング結果を検証"""
    
    # 元データを読み込み
    print("=== 元データ読み込み ===")
    original_df = pd.read_csv('anomart0727.csv')
    print(f"元データ行数: {len(original_df)}")
    
    # 修正版フィルタリング結果を読み込み
    print("\n=== 修正版フィルタリング結果読み込み ===")
    # 最新の出力ファイルを自動検出
    import glob
    latest_files = glob.glob('filtered_result_*.csv')
    if not latest_files:
        print("フィルタリング結果ファイルが見つかりません。")
        return
    
    latest_file = max(latest_files, key=os.path.getctime)
    print(f"検証対象ファイル: {latest_file}")
    filtered_df = pd.read_csv(latest_file)
    print(f"修正版フィルタリング結果行数: {len(filtered_df)}")
    
    # 1. 勝率フィルタの検証
    print("\n=== 勝率フィルタ検証 ===")
    # 勝率の列から%を除去して数値に変換
    original_df['勝率_30日_数値'] = original_df['勝率_30日'].str.replace('%', '').astype(float)
    
    # 85%以上のデータを抽出
    win_rate_filtered = original_df[original_df['勝率_30日_数値'] >= 85.0]
    print(f"勝率85%以上のデータ: {len(win_rate_filtered)}行")
    
    # フィルタリング結果と比較
    filtered_win_rates = filtered_df['勝率_30日'].str.replace('%', '').astype(float)
    min_win_rate = filtered_win_rates.min()
    max_win_rate = filtered_win_rates.max()
    print(f"修正版フィルタリング結果の勝率範囲: {min_win_rate}% - {max_win_rate}%")
    
    # 2. 日付情報を含めた時刻重複の検証
    print("\n=== 日付情報を含めた時刻重複検証 ===")
    
    # 元データから基準日情報を取得
    original_filtered = original_df[original_df['勝率_30日_数値'] >= 85.0].copy()
    
    # フィルタリング結果の各行について、元データから対応する行を特定
    filtered_df['エントリー日時'] = None
    filtered_df['クローズ日時'] = None
    
    for idx, row in filtered_df.iterrows():
        # 元データから同じ条件の行を検索
        matching_rows = original_filtered[
            (original_filtered['エントリー時刻'] == row['エントリー時刻']) &
            (original_filtered['クローズ時刻'] == row['クローズ時刻']) &
            (original_filtered['銘柄'] == row['銘柄']) &
            (original_filtered['方向'] == row['方向'])
        ]
        
        if len(matching_rows) > 0:
            base_date = matching_rows.iloc[0]['基準日']
            entry_dt, close_dt = parse_datetime_with_date(
                base_date, row['エントリー時刻'], row['クローズ時刻']
            )
            filtered_df.at[idx, 'エントリー日時'] = entry_dt
            filtered_df.at[idx, 'クローズ日時'] = close_dt
    
    # 日付情報を含めた時刻重複をチェック
    overlap_count = 0
    for i in range(len(filtered_df)):
        for j in range(i + 1, len(filtered_df)):
            entry1 = filtered_df.iloc[i]['エントリー日時']
            close1 = filtered_df.iloc[i]['クローズ日時']
            entry2 = filtered_df.iloc[j]['エントリー日時']
            close2 = filtered_df.iloc[j]['クローズ日時']
            
            if time_overlap_with_date(entry1, close1, entry2, close2):
                overlap_count += 1
                print(f"重複発見: {filtered_df.iloc[i]['エントリー時刻']}-{filtered_df.iloc[i]['クローズ時刻']} と {filtered_df.iloc[j]['エントリー時刻']}-{filtered_df.iloc[j]['クローズ時刻']}")
    
    print(f"日付情報を含めた時刻重複の数: {overlap_count}")
    
    # 3. 列の検証
    print("\n=== 列検証 ===")
    expected_columns = ['方向', '銘柄', 'エントリー時刻', 'クローズ時刻', '勝率_30日', '合計変動pips_30日']
    actual_columns = [col for col in filtered_df.columns if col not in ['エントリー日時', 'クローズ日時']]
    print(f"期待される列: {expected_columns}")
    print(f"実際の列: {actual_columns}")
    print(f"列が一致: {expected_columns == actual_columns}")
    
    # 4. データの統計情報
    print("\n=== データ統計 ===")
    print(f"銘柄の種類: {filtered_df['銘柄'].nunique()}")
    print(f"銘柄別件数:")
    print(filtered_df['銘柄'].value_counts())
    
    print(f"\n方向別件数:")
    print(filtered_df['方向'].value_counts())
    
    # 5. 時刻順ソートの検証
    print("\n=== 時刻順ソート検証 ===")
    is_sorted = filtered_df['エントリー日時'].is_monotonic_increasing
    print(f"エントリー時刻でソートされている: {is_sorted}")
    
    # 最初の5件と最後の5件を表示
    print("\n最初の5件:")
    print(filtered_df[['エントリー時刻', '銘柄', '方向']].head())
    
    print("\n最後の5件:")
    print(filtered_df[['エントリー時刻', '銘柄', '方向']].tail())
    
    # 6. 日をまたぐ取引の確認
    print("\n=== 日をまたぐ取引の確認 ===")
    for idx, row in filtered_df.iterrows():
        entry_time = datetime.strptime(row['エントリー時刻'], '%H:%M:%S').time()
        close_time = datetime.strptime(row['クローズ時刻'], '%H:%M:%S').time()
        
        if close_time < entry_time:
            print(f"日をまたぐ取引: {row['エントリー時刻']}-{row['クローズ時刻']} ({row['銘柄']})")

if __name__ == "__main__":
    verify_fixed_filtering() 