#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EURAUD処理修正の実証テストスクリプト
main.pyの修正版関数をテストする独立スクリプト
"""

import logging
import sys
from datetime import datetime

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('euraud_test.log', encoding='utf-8')
    ]
)

# テスト用のダミー関数（実際のAPIを使わないバージョン）
def mock_get_tickers(symbols):
    """
    モックティッカーデータ（テスト用）
    実際のAPIの代わりに固定値を返す
    """
    mock_data = {
        'EUR_AUD': {'symbol': 'EUR_AUD', 'bid': 1.6450, 'ask': 1.6460},
        'AUD_JPY': {'symbol': 'AUD_JPY', 'bid': 98.50, 'ask': 98.60},
        'EUR_JPY': {'symbol': 'EUR_JPY', 'bid': 162.10, 'ask': 162.20},
        'USD_JPY': {'symbol': 'USD_JPY', 'bid': 149.80, 'ask': 149.90},
        'EUR_USD': {'symbol': 'EUR_USD', 'bid': 1.0820, 'ask': 1.0830}
    }
    
    result = {'data': []}
    for symbol in symbols:
        if symbol in mock_data:
            result['data'].append(mock_data[symbol])
    
    return result

def detect_currency_pair_type(symbol):
    """通貨ペアタイプ判定"""
    if "JPY" in symbol:
        return "JPY"
    elif symbol.endswith("_USD"):
        return "USD"
    elif symbol.endswith("_AUD"):
        return "AUD"
    elif symbol.endswith("_EUR"):
        return "EUR"
    elif symbol.startswith("EUR_"):
        return "EUR_BASE"
    else:
        return "OTHER"

def get_audjpy_rate_mock():
    """AUD/JPYレート取得（モック版）"""
    try:
        tickers = mock_get_tickers(["AUD_JPY"])
        if tickers and 'data' in tickers:
            for item in tickers['data']:
                if item['symbol'] == 'AUD_JPY':
                    audjpy_rate = float(item['bid'])
                    logging.info(f"AUD/JPYレート取得成功（モック）: {audjpy_rate}")
                    return audjpy_rate
        return None
    except Exception as e:
        logging.error(f"AUD/JPYレート取得エラー（モック）: {e}")
        return None

def get_eurjpy_rate_mock():
    """EUR/JPYレート取得（モック版）"""
    try:
        tickers = mock_get_tickers(["EUR_JPY"])
        if tickers and 'data' in tickers:
            for item in tickers['data']:
                if item['symbol'] == 'EUR_JPY':
                    eurjpy_rate = float(item['bid'])
                    logging.info(f"EUR/JPYレート取得成功（モック）: {eurjpy_rate}")
                    return eurjpy_rate
        return None
    except Exception as e:
        logging.error(f"EUR/JPYレート取得エラー（モック）: {e}")
        return None

def calc_auto_lot_test(balance, symbol, side, leverage, risk_ratio=0.02):
    """
    修正版ロット計算のテスト版
    """
    try:
        safety_margin = 0.95
        balance_float = float(balance)
        leverage_float = float(leverage)
        
        # ティッカーデータ取得
        tickers = mock_get_tickers([symbol])
        if not tickers or 'data' not in tickers:
            raise ValueError("ティッカーデータの取得に失敗しました")
        
        # レート取得
        rate_data = None
        for item in tickers['data']:
            if item['symbol'] == symbol:
                rate_data = item
                break
        
        if not rate_data:
            raise ValueError(f"{symbol}のレート情報の取得に失敗しました")
        
        # 売買方向に応じたレート選択
        rate = float(rate_data['ask']) if side == "BUY" else float(rate_data['bid'])
        
        # 利用可能証拠金計算
        available_balance = balance_float * risk_ratio * safety_margin
        
        # 通貨ペアタイプ判定
        pair_type = detect_currency_pair_type(symbol)
        logging.info(f"通貨ペアタイプ判定: {symbol} -> {pair_type}")
        
        # 通貨ペアに応じた計算
        if pair_type == "JPY":
            volume = int((available_balance * leverage_float) / rate)
            logging.info(f"JPYペア計算: 円証拠金={available_balance}, レート={rate}, 計算結果={volume}")
            
        elif pair_type == "USD":
            usdjpy_tickers = mock_get_tickers(['USD_JPY'])
            usdjpy_rate = usdjpy_tickers['data'][0]['bid'] if usdjpy_tickers['data'] else 150.0
            available_balance_usd = available_balance / usdjpy_rate
            volume = int((available_balance_usd * leverage_float) / rate)
            logging.info(f"USDペア計算: 円証拠金={available_balance}, USD/JPY={usdjpy_rate}, USD証拠金={available_balance_usd}, 計算結果={volume}")
                
        elif pair_type == "AUD" or pair_type == "EUR_BASE":
            if pair_type == "AUD":
                cross_rate = get_audjpy_rate_mock()
                currency_name = "AUD"
            else:  # EUR_BASE (EUR_AUD等)
                cross_rate = get_eurjpy_rate_mock()
                currency_name = "EUR"
                
            if cross_rate and cross_rate > 0:
                available_balance_cross = available_balance / cross_rate
                volume = int((available_balance_cross * leverage_float) / rate)
                logging.info(f"{currency_name}ペア計算: 円証拠金={available_balance}, {currency_name}/JPY={cross_rate}, {currency_name}証拠金={available_balance_cross}, 計算結果={volume}")
            else:
                volume = int((available_balance * leverage_float) / rate)
                logging.warning(f"{currency_name}/JPYレート取得失敗、円基準で計算: {volume}")
                
        else:
            volume = int((available_balance * leverage_float) / rate)
            logging.warning(f"未対応通貨ペア({pair_type})、円基準で計算: {volume}")
        
        # 最小・最大制限
        volume = max(1, min(volume, 500000))
        
        return volume
        
    except Exception as e:
        logging.error(f"自動ロット計算エラー({symbol}): {e}")
        raise

def calculate_profit_test(entry_price, exit_price, side, symbol, size):
    """
    修正版損益計算のテスト版
    """
    try:
        pip_value = 0.01 if "JPY" in symbol else 0.0001
        
        # pips計算
        if side == "BUY":
            profit_pips = (exit_price - entry_price) / pip_value
        else:
            profit_pips = (entry_price - exit_price) / pip_value
        
        # 基本損益計算
        profit = profit_pips * float(size) * pip_value
        
        # 通貨ペアタイプ判定
        pair_type = detect_currency_pair_type(symbol)
        
        # 通貨別の円換算
        if pair_type == "JPY":
            final_profit = profit
            
        elif pair_type == "USD":
            usdjpy_tickers = mock_get_tickers(["USD_JPY"])
            usdjpy_rate = usdjpy_tickers['data'][0]['bid'] if usdjpy_tickers['data'] else 150.0
            final_profit = profit * usdjpy_rate
            
        elif pair_type == "AUD":
            audjpy_rate = get_audjpy_rate_mock()
            final_profit = profit * audjpy_rate if audjpy_rate else profit
            
        elif pair_type == "EUR_BASE":
            eurjpy_rate = get_eurjpy_rate_mock()
            final_profit = profit * eurjpy_rate if eurjpy_rate else profit
            
        else:
            final_profit = profit
        
        logging.info(f"損益計算詳細: エントリー={entry_price}, 決済={exit_price}, 方向={side}, ロット={size}, pips={profit_pips:.2f}, 最終損益={final_profit:.2f}円")
        
        return round(final_profit, 2)
        
    except Exception as e:
        logging.error(f"損益計算エラー({symbol}): {e}")
        return 0.0

def run_euraud_test():
    """
    EURAUD処理の実証テスト実行
    """
    print("=" * 60)
    print("EURAUD処理修正の実証テスト")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # テストケース
    test_cases = [
        {
            "name": "EURAUD - 基本ケース",
            "symbol": "EUR_AUD",
            "balance": 100000,
            "leverage": 15,
            "side": "BUY",
            "entry_price": 1.6450,
            "exit_price": 1.6470,
            "size": 1000
        },
        {
            "name": "EURAUD - 売りケース",
            "symbol": "EUR_AUD",
            "balance": 100000,
            "leverage": 15,
            "side": "SELL",
            "entry_price": 1.6460,
            "exit_price": 1.6440,
            "size": 1000
        },
        {
            "name": "EURUSD - 比較用",
            "symbol": "EUR_USD",
            "balance": 100000,
            "leverage": 15,
            "side": "BUY",
            "entry_price": 1.0820,
            "exit_price": 1.0840,
            "size": 1000
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n【テストケース {i}: {case['name']}】")
        print(f"通貨ペア: {case['symbol']}")
        print(f"証拠金: {case['balance']:,}円")
        print(f"レバレッジ: {case['leverage']}倍")
        print(f"売買方向: {case['side']}")
        
        try:
            # 1. 通貨ペアタイプ判定
            pair_type = detect_currency_pair_type(case['symbol'])
            print(f"通貨ペアタイプ: {pair_type}")
            
            # 2. ロット計算
            calculated_lot = calc_auto_lot_test(
                case['balance'], case['symbol'], case['side'], case['leverage']
            )
            print(f"計算ロット数: {calculated_lot:,}")
            
            # 3. 損益計算
            profit = calculate_profit_test(
                case['entry_price'], case['exit_price'], 
                case['side'], case['symbol'], case['size']
            )
            print(f"損益計算: {profit:,.2f}円")
            
            # 4. 参考値計算
            pip_value = 0.01 if "JPY" in case['symbol'] else 0.0001
            pip_diff = (case['exit_price'] - case['entry_price']) / pip_value
            if case['side'] == "SELL":
                pip_diff = -pip_diff
            print(f"pips差: {pip_diff:.1f}pips")
            
        except Exception as e:
            print(f"テストエラー: {e}")
    
    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

if __name__ == "__main__":
    run_euraud_test() 