/**
 * Google Drive上のCSVファイルを処理するGoogle Apps Script
 * 
 * 使用方法:
 * 1. Google Apps Scriptエディタでこのコードを貼り付け
 * 2. 必要なライブラリを追加（CSV処理用）
 * 3. 実行ボタンをクリック
 */

// 設定
const CONFIG = {
  win_rate_threshold: 85.0,
  default_input_file: "20250720.csv",
  output_columns: ["方向", "銘柄", "エントリー時刻", "クローズ時刻", "勝率_30日", "合計変動pips_30日"]
};

/**
 * メイン処理関数
 */
function processCSV() {
  try {
    // Google Driveからファイルを取得
    const inputFile = getFileByName(CONFIG.default_input_file);
    if (!inputFile) {
      throw new Error(`ファイル '${CONFIG.default_input_file}' が見つかりません`);
    }
    
    console.log("=== CSV処理開始 ===");
    console.log(`入力ファイル: ${inputFile.getName()}`);
    console.log(`勝率閾値: ${CONFIG.win_rate_threshold}%`);
    
    // CSVを読み込み
    const csvContent = inputFile.getBlob().getDataAsString('UTF-8');
    const rows = Utilities.parseCsv(csvContent);
    
    if (rows.length < 2) {
      throw new Error("CSVファイルが空またはヘッダーのみです");
    }
    
    const headers = rows[0];
    const dataRows = rows.slice(1);
    
    console.log(`元のデータ行数: ${dataRows.length}`);
    
    // 勝率の列インデックスを取得
    const winRateIndex = headers.indexOf('勝率_30日');
    const entryTimeIndex = headers.indexOf('エントリー時刻');
    const closeTimeIndex = headers.indexOf('クローズ時刻');
    const pipsIndex = headers.indexOf('合計変動pips_30日');
    
    if (winRateIndex === -1) {
      throw new Error("勝率_30日の列が見つかりません");
    }
    
    // 1. 勝率フィルタリング
    const filteredRows = dataRows.filter(row => {
      const winRateStr = row[winRateIndex];
      const winRate = parseFloat(winRateStr.replace('%', ''));
      return winRate >= CONFIG.win_rate_threshold;
    });
    
    console.log(`勝率${CONFIG.win_rate_threshold}%以上フィルタ後: ${filteredRows.length}行`);
    
    // 2. 時刻解析と重複除去
    const processedRows = [];
    const indicesToRemove = new Set();
    
    for (let i = 0; i < filteredRows.length; i++) {
      if (indicesToRemove.has(i)) continue;
      
      const row1 = filteredRows[i];
      const entryTime1 = parseTime(row1[entryTimeIndex]);
      const closeTime1 = parseTime(row1[closeTimeIndex]);
      const winRate1 = parseFloat(row1[winRateIndex].replace('%', ''));
      const pips1 = parseFloat(row1[pipsIndex]);
      
      if (!entryTime1 || !closeTime1) continue;
      
      for (let j = i + 1; j < filteredRows.length; j++) {
        if (indicesToRemove.has(j)) continue;
        
        const row2 = filteredRows[j];
        const entryTime2 = parseTime(row2[entryTimeIndex]);
        const closeTime2 = parseTime(row2[closeTimeIndex]);
        const winRate2 = parseFloat(row2[winRateIndex].replace('%', ''));
        const pips2 = parseFloat(row2[pipsIndex]);
        
        if (!entryTime2 || !closeTime2) continue;
        
        // 時刻重複チェック
        if (timeOverlap(entryTime1, closeTime1, entryTime2, closeTime2)) {
          // 勝率比較
          if (winRate1 > winRate2) {
            indicesToRemove.add(j);
          } else if (winRate1 < winRate2) {
            indicesToRemove.add(i);
          } else {
            // 勝率が同じ場合はpips比較
            if (pips1 < pips2) {
              indicesToRemove.add(i);
            } else {
              indicesToRemove.add(j);
            }
          }
        }
      }
    }
    
    // 重複行を除去
    const finalRows = filteredRows.filter((_, index) => !indicesToRemove.has(index));
    console.log(`重複除去後: ${finalRows.length}行`);
    
    // 3. エントリー時刻でソート
    finalRows.sort((a, b) => {
      const timeA = parseTime(a[entryTimeIndex]);
      const timeB = parseTime(b[entryTimeIndex]);
      return timeA - timeB;
    });
    
    // 4. 出力用の列を選択
    const outputHeaders = CONFIG.output_columns;
    const outputRows = finalRows.map(row => {
      return outputHeaders.map(header => {
        const index = headers.indexOf(header);
        return index !== -1 ? row[index] : '';
      });
    });
    
    // 5. 結果を保存
    const today = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const outputFileName = `filtered_result_${today}.csv`;
    
    const outputContent = [outputHeaders, ...outputRows];
    const csvOutput = outputContent.map(row => row.join(',')).join('\n');
    
    const outputFile = DriveApp.createFile(outputFileName, csvOutput, MimeType.CSV);
    
    console.log("=== 処理結果 ===");
    console.log(`最終行数: ${outputRows.length}`);
    console.log(`出力ファイル: ${outputFile.getName()}`);
    console.log(`ファイルID: ${outputFile.getId()}`);
    
    // 最初の10行を表示
    console.log("=== 最初の10行 ===");
    outputRows.slice(0, 10).forEach((row, index) => {
      const entryTime = row[outputHeaders.indexOf('エントリー時刻')];
      const closeTime = row[outputHeaders.indexOf('クローズ時刻')];
      const symbol = row[outputHeaders.indexOf('銘柄')];
      const direction = row[outputHeaders.indexOf('方向')];
      const winRate = row[outputHeaders.indexOf('勝率_30日')];
      const pips = row[outputHeaders.indexOf('合計変動pips_30日')];
      
      console.log(`${index + 1}. 時刻: ${entryTime}-${closeTime}, 銘柄: ${symbol}, 方向: ${direction}, 勝率30日: ${winRate}, 合計変動pips: ${pips}`);
    });
    
    return outputFile;
    
  } catch (error) {
    console.error("エラーが発生しました:", error.message);
    throw error;
  }
}

/**
 * ファイル名でファイルを検索
 */
function getFileByName(fileName) {
  const files = DriveApp.getFilesByName(fileName);
  if (files.hasNext()) {
    return files.next();
  }
  return null;
}

/**
 * 時刻文字列を解析
 */
function parseTime(timeStr) {
  try {
    const parts = timeStr.split(':');
    if (parts.length === 3) {
      const hours = parseInt(parts[0]);
      const minutes = parseInt(parts[1]);
      const seconds = parseInt(parts[2]);
      return hours * 3600 + minutes * 60 + seconds; // 秒数に変換
    }
  } catch (e) {
    // 解析エラー
  }
  return null;
}

/**
 * 時間帯の重複チェック
 */
function timeOverlap(start1, end1, start2, end2) {
  return start1 <= end2 && start2 <= end1;
}

/**
 * テスト用関数
 */
function testProcess() {
  try {
    const result = processCSV();
    console.log("処理が正常に完了しました");
    return result;
  } catch (error) {
    console.error("テスト実行でエラーが発生しました:", error);
  }
} 