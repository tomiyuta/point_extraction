@echo off
REM point_extraction フィルタリング実行スクリプト（修正版）
REM 使用方法: run_filtering.bat [入力ファイル] [出力ファイル] [勝率閾値]

echo === point_extraction フィルタリング開始 ===
echo 日時: %date% %time%

REM 仮想環境の確認とアクティベート
if not exist "venv" (
    echo 仮想環境が見つかりません。作成中...
    python -m venv venv
)

echo 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

REM 必要なライブラリの確認とインストール
echo 必要なライブラリを確認中...
pip install pandas numpy

REM 引数の処理
set INPUT_FILE=%1
set OUTPUT_FILE=%2
set WIN_RATE=%3

echo === 実行パラメータ ===
if "%INPUT_FILE%"=="" (
    echo 入力ファイル: 設定ファイルから自動取得
) else (
    echo 入力ファイル: %INPUT_FILE%
)

if "%OUTPUT_FILE%"=="" (
    echo 出力ファイル: 自動生成
) else (
    echo 出力ファイル: %OUTPUT_FILE%
)

if "%WIN_RATE%"=="" (
    echo 勝率閾値: 設定ファイルから自動取得%%
) else (
    echo 勝率閾値: %WIN_RATE%%%
)

echo.
echo === フィルタリング処理開始 ===

REM 修正版スクリプトの実行
if not "%INPUT_FILE%"=="" if not "%OUTPUT_FILE%"=="" if not "%WIN_RATE%"=="" (
    REM 全パラメータ指定
    python process_csv_weekly_fixed.py "%INPUT_FILE%" "%OUTPUT_FILE%" "%WIN_RATE%"
) else if not "%INPUT_FILE%"=="" if not "%OUTPUT_FILE%"=="" (
    REM 入力ファイルと出力ファイル指定
    python process_csv_weekly_fixed.py "%INPUT_FILE%" "%OUTPUT_FILE%"
) else if not "%INPUT_FILE%"=="" (
    REM 入力ファイルのみ指定
    python process_csv_weekly_fixed.py "%INPUT_FILE%"
) else (
    REM 設定ファイルから自動取得
    python process_csv_weekly_fixed.py
)

REM 実行結果の確認
if %errorlevel% equ 0 (
    echo.
    echo === 処理完了 ===
    echo 日時: %date% %time%
    
    REM 最新の出力ファイルを確認
    for /f "delims=" %%i in ('dir /b /od filtered_result_*.csv 2^>nul') do set LATEST_FILE=%%i
    if defined LATEST_FILE (
        echo 最新の出力ファイル: %LATEST_FILE%
        for %%A in (%LATEST_FILE%) do echo ファイルサイズ: %%~zA bytes
    )
) else (
    echo.
    echo === エラーが発生しました ===
    exit /b 1
)

pause 