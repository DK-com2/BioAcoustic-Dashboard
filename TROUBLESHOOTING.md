# トラブルシューティングガイド

このドキュメントでは、BioAcoustic Dashboard使用時によくある問題と解決方法を説明します。

## 起動時の問題

### アプリケーション起動エラー: 0

**症状:** `streamlit run app.py` で起動時にエラーコード0で終了

**原因と解決方法:**

1. **Pythonパッケージの不整合**
   ```bash
   # 仮想環境の再作成
   rm -rf venv  # Linux/macOS
   rmdir /s venv  # Windows
   
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate  # Windows
   
   pip install -r requirements.txt
   ```

2. **ポート競合**
   ```bash
   # 別ポートで起動
   streamlit run app.py --server.port 8502
   ```

3. **権限問題**
   ```bash
   # Linux/macOS
   chmod +x app.py
   
   # Windows: 管理者権限でコマンドプロンプト実行
   ```

### 設定エラー: データベースパスが正しく設定されていません

**症状:** 設定ファイルが見つからないか、パスが不正

**解決手順:**

1. **設定ファイル再作成**
   ```bash
   python setup_config.py
   ```

2. **手動設定確認**
   ```bash
   # config.jsonの存在確認
   ls config.json  # Linux/macOS  
   dir config.json  # Windows
   
   # 内容確認
   cat config.json  # Linux/macOS
   type config.json  # Windows
   ```

3. **パス形式の確認**
   ```json
   // 間違い（Windows）
   "database_path": "C:\BirdNET\database"
   
   // 正しい（Windows） 
   "database_path": "C:\\BirdNET\\database"
   // または
   "database_path": "C:/BirdNET/database"
   ```

### データベースファイルが見つかりません

**症状:** `result.db`が見つからない

**解決手順:**

1. **ファイル存在確認**
   ```bash
   # データベースファイル検索
   find /path/to/search -name "*.db" 2>/dev/null  # Linux/macOS
   dir /s *.db  # Windows
   ```

2. **サポートするファイル名**
   - `result.db`
   - `birdnet_simple.db`
   - `birdnet.db` 
   - `birds.db`

3. **テスト用データベース作成**
   ```python
   # create_test_db.py
   import sqlite3
   import os
   
   os.makedirs('database', exist_ok=True)
   conn = sqlite3.connect('database/result.db')
   cursor = conn.cursor()
   
   cursor.execute('''
   CREATE TABLE bird_detections (
       id INTEGER PRIMARY KEY,
       session_name TEXT NOT NULL,
       filename TEXT NOT NULL,
       start_time_seconds REAL NOT NULL,
       end_time_seconds REAL NOT NULL,
       common_name TEXT,
       confidence REAL NOT NULL
   )
   ''')
   
   cursor.execute('''
   INSERT INTO bird_detections 
   VALUES (1, 'test', 'test.wav', 0.0, 3.0, 'Test Bird', 0.95)
   ''')
   
   conn.commit()
   conn.close()
   ```

## データベース関連の問題

### データベースがロックされています

**症状:** `database is locked` エラー

**解決方法:**

1. **他のプロセス確認・終了**
   ```bash
   # Linux/macOS
   lsof database/result.db
   kill -9 <PID>
   
   # Windows  
   handle database\result.db
   taskkill /F /PID <PID>
   ```

2. **ロックファイル削除**
   ```bash
   rm database/result.db-wal database/result.db-shm
   ```

3. **データベース整合性チェック**
   ```bash
   sqlite3 database/result.db "PRAGMA integrity_check;"
   ```

### テーブルが存在しません

**症状:** `no such table: bird_detections`

**解決方法:**

1. **テーブル構造確認**
   ```bash
   sqlite3 database/result.db ".tables"
   sqlite3 database/result.db ".schema"
   ```

2. **必要なカラム確認**
   ```sql
   PRAGMA table_info(bird_detections);
   ```

3. **テーブル作成**
   ```sql
   CREATE TABLE bird_detections (
       id INTEGER PRIMARY KEY,
       session_name TEXT NOT NULL,
       filename TEXT NOT NULL,
       start_time_seconds REAL NOT NULL,
       end_time_seconds REAL NOT NULL,
       common_name TEXT,
       confidence REAL NOT NULL,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

### 品質評価カラムエラー

**症状:** `no such column: quality_status`

**解決方法:**

品質評価ボタンを一度クリックすると自動的にカラムが追加されます。または手動で追加：

```sql
sqlite3 database/result.db
ALTER TABLE bird_detections 
ADD COLUMN quality_status TEXT DEFAULT 'pending' 
CHECK(quality_status IN ('pending', 'approved', 'rejected'));

ALTER TABLE bird_detections 
ADD COLUMN reviewed_at TIMESTAMP;
```

## 音声・画像処理の問題

### 音声ファイルが再生できません

**症状:** 音声プレイヤーでエラーまたは無音

**原因別解決法:**

1. **ファイル形式問題**
   ```bash
   # ffmpegでWAVに変換
   ffmpeg -i input.mp3 -ar 22050 -ac 1 output.wav
   ```

2. **ファイルパス問題**
   ```python
   # パスの存在確認
   import os
   print(os.path.exists('path/to/audio/file.wav'))
   ```

3. **権限問題**
   ```bash
   # ファイル権限確認・変更
   chmod 644 audio_segments/*.wav  # Linux/macOS
   ```

4. **ブラウザ問題**
   - Chrome、Firefox、Safariで確認
   - ブラウザの音声設定確認
   - アドブロッカーの無効化

### スペクトログラムが表示されません

**症状:** 画像生成ボタンを押してもスペクトログラムが表示されない

**解決手順:**

1. **依存関係確認**
   ```bash
   pip install --upgrade matplotlib librosa
   ```

2. **手動生成テスト**
   ```python
   import librosa
   import matplotlib.pyplot as plt
   import numpy as np
   
   # テスト用スペクトログラム生成
   y, sr = librosa.load('test.wav', sr=22050)
   D = librosa.stft(y)
   S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
   
   plt.figure(figsize=(10, 4))
   librosa.display.specshow(S_db, sr=sr, x_axis='time', y_axis='hz')
   plt.colorbar(format='%+2.0f dB')
   plt.title('Spectrogram')
   plt.savefig('test_spectrogram.png')
   plt.close()
   ```

3. **出力ディレクトリ確認**
   ```bash
   # ディレクトリ権限確認
   ls -la database/spectrograms/  # Linux/macOS
   dir database\spectrograms  # Windows
   
   # 権限修正
   chmod 755 database/spectrograms/  # Linux/macOS
   ```

### ファイル生成が失敗します

**症状:** 音声・画像生成ボタンでエラー

**デバッグ手順:**

1. **エラー詳細の確認**
   ```python
   # デバッグモードで実行
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **メモリ使用量確認**
   ```bash
   # メモリ不足の可能性
   free -h  # Linux
   wmic OS get TotalVisibleMemorySize,FreePhysicalMemory  # Windows
   ```

3. **一時ファイル削除**
   ```bash
   # 一時ファイルクリア
   rm -rf /tmp/librosa_*  # Linux/macOS
   del /tmp /Q  # Windows
   ```

## パッケージ・依存関係の問題

### ImportError: No module named 'xxx'

**症状:** Pythonモジュールのインポートエラー

**解決手順:**

1. **仮想環境確認**
   ```bash
   # 仮想環境のアクティベート確認
   which python  # Linux/macOS
   where python  # Windows
   ```

2. **パッケージ再インストール**
   ```bash
   pip install -r requirements.txt --force-reinstall --no-cache-dir
   ```

3. **個別パッケージ確認**
   ```bash
   pip list | grep <package-name>
   pip install --upgrade <package-name>
   ```

### librosa warning: pkg_resources is deprecated

**症状:** librosa使用時の警告メッセージ

**解決方法:**
```bash
pip install --upgrade librosa setuptools pip
```

### DLL load failed (Windows)

**症状:** Windowsでライブラリロードエラー

**解決方法:**

1. **Microsoft Visual C++ 再頒布可能パッケージ**
   - Visual Studio Build Tools インストール
   - または Microsoft C++ Build Tools

2. **conda環境使用**
   ```bash
   conda create -n birdnet python=3.10
   conda activate birdnet
   conda install -c conda-forge librosa streamlit pandas
   ```

## ネットワーク・アクセスの問題

### ポート 8501 は既に使用されています

**症状:** 既にポートが使用中

**解決方法:**

1. **別ポート使用**
   ```bash
   streamlit run app.py --server.port 8502
   ```

2. **プロセス終了**
   ```bash
   # Linux/macOS
   lsof -ti:8501 | xargs kill
   
   # Windows
   netstat -ano | findstr :8501
   taskkill /F /PID <PID>
   ```

### アクセス権限エラー

**症状:** Streamlitアプリへのアクセスが拒否される

**解決方法:**

1. **ファイアウォール設定**
   ```bash
   # Linux (ufw)
   sudo ufw allow 8501
   
   # Windows: Windows Defenderファイアウォールで許可
   ```

2. **ホスト設定変更**
   ```bash
   streamlit run app.py --server.address 0.0.0.0
   ```

## ブラウザ・UI の問題

### レスポンシブ表示の問題

**症状:** モバイル・タブレットで表示が崩れる

**解決方法:**

1. **ブラウザキャッシュクリア**
   - Ctrl+F5 (Windows)
   - Cmd+Shift+R (macOS)

2. **ブラウザ変更**
   - Chrome、Firefox、Safari で確認

3. **CSS調整**
   ```python
   # カスタムCSS追加
   st.markdown("""
   <style>
   @media (max-width: 768px) {
       .main .block-container {
           padding: 1rem;
       }
   }
   </style>
   """, unsafe_allow_html=True)
   ```

### テーブル表示の問題

**症状:** テーブルが正しく表示されない

**解決方法:**

1. **データ型確認**
   ```python
   print(df.dtypes)
   print(df.head())
   ```

2. **キャッシュクリア**
   ```python
   st.cache_data.clear()
   st.rerun()
   ```

3. **ブラウザリロード**
   - F5またはCtrl+R

## パフォーマンスの問題

### アプリケーションが遅い

**症状:** データ読み込みや処理が遅い

**最適化方法:**

1. **データベースインデックス**
   ```sql
   CREATE INDEX idx_session_name ON bird_detections(session_name);
   CREATE INDEX idx_common_name ON bird_detections(common_name);
   CREATE INDEX idx_confidence ON bird_detections(confidence);
   ```

2. **Streamlitキャッシュ活用**
   ```python
   @st.cache_data(ttl=3600)
   def load_data():
       # データ読み込み処理
       return data
   ```

3. **メモリ使用量削減**
   ```python
   # 大きなDataFrameを分割処理
   chunk_size = 1000
   for chunk in pd.read_sql(query, conn, chunksize=chunk_size):
       process_chunk(chunk)
   ```

### メモリ不足エラー

**症状:** `MemoryError` またはシステムが不安定

**解決方法:**

1. **メモリ使用量確認**
   ```python
   import psutil
   print(f"Memory usage: {psutil.virtual_memory().percent}%")
   ```

2. **処理の分割**
   ```python
   # バッチ処理でメモリ使用量削減
   batch_size = 100
   for i in range(0, len(detection_ids), batch_size):
       batch = detection_ids[i:i+batch_size]
       process_batch(batch)
   ```

## サポートとヘルプ

### 問題診断の手順

1. **環境情報収集**
   ```bash
   python --version
   pip list
   streamlit version
   uname -a  # Linux/macOS
   systeminfo  # Windows
   ```

2. **ログファイル確認**
   ```bash
   # Streamlitログ
   ~/.streamlit/logs/
   
   # アプリケーションログ
   tail -f app.log
   ```

3. **最小再現例作成**
   ```python
   # 問題を再現する最小限のコード
   import streamlit as st
   st.write("Hello World")
   ```

### Issue報告時の必要情報

問題報告時には以下の情報を含めてください：

1. **環境情報**
   - OS とバージョン
   - Pythonバージョン
   - パッケージバージョン (`pip list`)

2. **問題の詳細**
   - 具体的なエラーメッセージ
   - 再現手順
   - 期待する結果と実際の結果

3. **設定情報**
   - `config.json`の内容（センシティブ情報は除く）
   - データベースの構造
   - 使用しているデータのサンプル

### 緊急時の対処

**アプリケーションが完全に動かない場合:**

1. **最小構成で起動**
   ```bash
   streamlit hello  # Streamlit動作確認
   ```

2. **設定リセット**
   ```bash
   rm config.json
   python setup_config.py
   ```

3. **クリーンインストール**
   ```bash
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install streamlit
   streamlit hello
   ```

---

このガイドで解決できない問題がある場合は、[Issues](../../issues) で詳細な情報とともに報告してください。