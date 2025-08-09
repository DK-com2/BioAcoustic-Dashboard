# セットアップガイド

このドキュメントでは、BioAcoustic Dashboardの詳細なセットアップ手順を説明します。

## システム要件

### 必須要件
- **Python**: 3.9 以上（3.10推奨）
- **メモリ**: 最低4GB（音声処理時は8GB推奨）
- **ストレージ**: 最低1GB（生成ファイル用に追加容量が必要）
- **OS**: Windows 10+、macOS 10.15+、Linux（Ubuntu 20.04+）

### 推奨環境
- **CPU**: マルチコア（音声処理の高速化）
- **ブラウザ**: Chrome 90+、Firefox 88+、Safari 14+

## インストール手順

### Step 1: Pythonの確認

```bash
python --version
# または
python3 --version
```

Python 3.9以上であることを確認してください。

### Step 2: リポジトリの取得

```bash
git clone <repository-url>
cd BioAcoustic-Dashboard
```

### Step 3: 仮想環境の作成

#### Windows (PowerShell/Command Prompt)
```cmd
python -m venv venv
venv\\Scripts\\activate
```

#### macOS/Linux (Bash/Zsh)
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 4: 依存パッケージのインストール

```bash
# 仮想環境が有効化されていることを確認
pip install --upgrade pip
pip install -r requirements.txt
```

#### パッケージインストールのトラブルシューティング

**Windows で audio processing でエラーが出る場合:**
```cmd
# Microsoft Visual C++ Build Tools が必要
pip install --upgrade setuptools wheel
pip install -r requirements.txt
```

**macOS で librosa インストールエラーの場合:**
```bash
# Homebrew経由でlibsndfileをインストール
brew install libsndfile
pip install -r requirements.txt
```

**Linux で audio dependencies エラーの場合:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install libsndfile1-dev ffmpeg

# CentOS/RHEL
sudo yum install libsndfile-devel ffmpeg
```

## 設定手順

### 方法1: セットアップスクリプト（推奨）

```bash
python setup_config.py
```

対話的に以下を設定します：
1. **データベースフォルダ**: BirdNETのresult.dbがある場所
2. **音声フォルダ**: 元音声ファイルがある場所  
3. **ホスト・ポート**: アプリケーション設定

#### セットアップスクリプトの詳細操作

```
BirdNET Streamlit Viewer 初期設定
============================================================

データベースフォルダの設定
   BirdNETのデータベースファイル（result.db等）があるフォルダを指定してください

データベースフォルダの絶対パスを入力: C:\path\to\your\database
パスを検証中: C:\path\to\your\database
データベースファイルを発見: result.db

音声フォルダの設定
   デフォルト: C:\path\to\your\database\audio
音声フォルダのパス (Enter でデフォルト): 

アプリケーション設定
ポート番号 (デフォルト: 8501): 
ホスト (デフォルト: localhost): 

設定ファイル config.json を作成しました
```

### 方法2: 手動設定

プロジェクトルートに `config.json` を作成：

```json
{
  "database_path": "/path/to/your/birdnet/database",
  "audio_path": "/path/to/your/birdnet/database/audio", 
  "app_settings": {
    "port": 8501,
    "host": "localhost"
  },
  "version": "1.0.0"
}
```

#### パスの指定方法

**Windows:**
```json
{
  "database_path": "C:\\\\path\\\\to\\\\your\\\\database",
  "audio_path": "C:\\\\path\\\\to\\\\your\\\\database\\\\audio"
}
```

**macOS/Linux:**
```json
{
  "database_path": "/path/to/your/database",
  "audio_path": "/path/to/your/database/audio"
}
```

### 方法3: 環境変数

一時的な設定や開発環境で使用：

**Windows:**
```cmd
set BIRDNET_DATABASE_PATH=C:\path\to\your\database
set BIRDNET_AUDIO_PATH=C:\path\to\your\database\audio
```

**macOS/Linux:**
```bash
export BIRDNET_DATABASE_PATH="/path/to/your/database"
export BIRDNET_AUDIO_PATH="/path/to/your/database/audio"
```

## データベース準備

### 重要：データベースの外部配置について

**このアプリケーションの重要な特徴として、データベースファイルをアプリケーション内にコピーする必要がありません。**

既存のBirdNETプロジェクトのデータベースを、元の場所にそのまま残して使用できます：

#### 利点
- **既存プロジェクトを保持**: BirdNETで作成したプロジェクト構造をそのまま維持
- **複数プロジェクト対応**: 設定変更だけで異なるプロジェクトのデータベースを切り替え
- **ストレージ効率**: 大容量のデータベースをコピーする必要なし
- **データ整合性**: 元のデータが変更されることなく安全に参照

#### 実際の使用例
```
# 既存のBirdNETプロジェクト（元の場所にそのまま）
D:/Research/BirdNet_Projects/Forest_Study_2024/
├── result.db                    ← このDBを直接参照
├── audio/
│   ├── original_recordings/
│   └── processed/
└── outputs/

# このダッシュボードアプリ（別の場所に配置）
C:/Tools/BioAcoustic-Dashboard/
├── config.json                 ← 上記パスを設定
├── app.py
└── streamlit_viewer/
```

### BirdNETの解析結果がある場合

既存の `result.db` または類似名のSQLiteファイルを **元の場所で** 使用できます：

1. **サポートするファイル名:**
   - `result.db`
   - `birdnet_simple.db` 
   - `birdnet.db`
   - `birds.db`

2. **必須テーブル:** `bird_detections`

3. **必須カラム:**
   ```sql
   id INTEGER PRIMARY KEY
   session_name TEXT NOT NULL
   filename TEXT NOT NULL  
   start_time_seconds REAL NOT NULL
   end_time_seconds REAL NOT NULL
   common_name TEXT
   confidence REAL NOT NULL
   ```

### サンプルデータベースを作成する場合

テスト用のデータベースを作成：

```python
import sqlite3
import os

# データベースディレクトリを作成
os.makedirs('database', exist_ok=True)

# データベース作成
conn = sqlite3.connect('database/result.db')
cursor = conn.cursor()

# テーブル作成
cursor.execute('''
CREATE TABLE IF NOT EXISTS bird_detections (
    id INTEGER PRIMARY KEY,
    session_name TEXT NOT NULL,
    model_name TEXT,
    filename TEXT NOT NULL,
    start_time_seconds REAL NOT NULL,  
    end_time_seconds REAL NOT NULL,
    scientific_name TEXT,
    common_name TEXT,
    confidence REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# サンプルデータ挿入
sample_data = [
    ('test_session', 'BirdNET', 'test_audio.wav', 10.0, 13.0, 'Turdus migratorius', 'American Robin', 0.95),
    ('test_session', 'BirdNET', 'test_audio.wav', 45.2, 48.5, 'Poecile atricapillus', 'Black-capped Chickadee', 0.87)
]

cursor.executemany('''
INSERT INTO bird_detections 
(session_name, model_name, filename, start_time_seconds, end_time_seconds, scientific_name, common_name, confidence)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', sample_data)

conn.commit()
conn.close()

print("Sample database created: database/result.db")
```

## 起動方法

### 標準起動

```bash
python app.py
```

### Streamlit直接起動

```bash
streamlit run app.py --server.port 8501
```

### 設定を指定して起動

```bash
streamlit run app.py --server.port 8080 --server.address 0.0.0.0
```

### Windows用バッチファイル

`start_viewer.bat` を使用：

```cmd
start_viewer.bat
```

## 起動確認

1. **ブラウザアクセス:** http://localhost:8501
2. **正常起動の確認:**
   - BirdNET データベースビューワーのタイトル表示
   - サイドバーに検索・フィルタ機能
   - エラーメッセージがないこと

3. **機能テスト:**
   - 検索実行ボタンクリック
   - データテーブルの表示確認
   - テーブル行選択でプレビュー表示

## トラブルシューティング

### 設定関連エラー

**Error: 設定エラー: データベースパスが正しく設定されていません**

```bash
# 設定を再作成
python setup_config.py

# または手動で config.json を確認
```

**Error: データベースファイルが見つかりません**

```bash
# パスの存在確認
ls /path/to/database/     # Linux/macOS
dir C:\path\to\database   # Windows

# 設定確認
python setup_config.py --show
```

### データベース関連エラー

**Error: no such table: bird_detections**

```sql
-- SQLiteで確認
sqlite3 database/result.db
.tables
.schema bird_detections
```

**Error: database is locked**

```bash
# 他のプロセスが使用中の可能性
lsof database/result.db  # Linux/macOS
# プロセス終了後に再実行
```

### パッケージ関連エラー

**ImportError: No module named 'xxx'**

```bash
# 仮想環境の確認
which python  # Linux/macOS
where python  # Windows

# パッケージ再インストール
pip install -r requirements.txt --force-reinstall
```

**librosa warning: pkg_resources is deprecated**

```bash
# librosa更新
pip install --upgrade librosa setuptools
```

### ネットワーク関連エラー

**Port 8501 already in use**

```bash
# ポート変更
streamlit run app.py --server.port 8502

# または既存プロセス終了
lsof -ti:8501 | xargs kill  # Linux/macOS
netstat -ano | findstr :8501  # Windows
```

## 開発環境セットアップ

開発者向けの追加セットアップ：

```bash
# 開発用パッケージのインストール
pip install pytest black flake8 jupyter

# コード整形
black streamlit_viewer/
black lib/

# テスト実行  
pytest tests/ -v

# Jupyter notebook起動（データ解析用）
jupyter notebook
```

## アップデート手順

既存インストールのアップデート：

```bash
# リポジトリ更新
git pull origin main

# 依存関係更新
pip install -r requirements.txt --upgrade

# 設定確認（必要に応じて）
python setup_config.py --show
```

---

これで基本的なセットアップは完了です。使用方法については [README.md](README.md) の「使用方法」セクションを参照してください。