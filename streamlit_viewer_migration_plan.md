# BirdNET Streamlit ビューワー独立リポジトリ作成計画

## 概要
BirdNET-SQLリポジトリ内のstreamlit_viewerを新しい独立リポジトリとして分離する作業計画です。
既存のdatabaseフォルダは使い回し、絶対パス設定で参照する方式に変更します。

## 1. ファイル・ディレクトリのコピー作業

### コピーが必要なファイル

#### streamlit_viewer/ ディレクトリ
```
streamlit_viewer/
├── config.py                           # 設定管理（要修正）
├── db_viewer.py                        # メインアプリケーション（要修正）
├── utils/
│   ├── __init__.py
│   └── audio_processor.py
├── audio_detail_backup.py              # バックアップファイル（任意）
├── CHANGELOG_GENERATION_ADDED.md
├── CHANGELOG_REMOVAL.md
├── CHANGELOG_TABLE_IMPROVEMENT.md
├── README_PHASE2.md
└── README_PHASE2_VIEWER.md
```

#### lib/ ディレクトリから必要な部分
```
lib/
├── db/
│   ├── __init__.py
│   ├── database.py                     # BirdNetSimpleDB クラス
│   └── session_manager.py              # セッション管理（必要に応じて）
└── audio_processing/                   # 音声処理モジュール全体
    ├── __init__.py
    ├── file_manager.py
    ├── processing_manager.py
    ├── segment_generator.py
    └── spectrogram_generator.py
```

#### ルートファイル
```
requirements.txt                        # Python依存関係
start_streamlit_viewer.bat             # 起動スクリプト（要修正）
```

## 2. 設定ファイルの修正

### 2.1 config.py の修正内容

#### 現在の問題点
- 相対パスでプロジェクトルートを取得
- databaseフォルダが固定パス

#### 修正内容
```python
# 修正前
def get_project_root() -> Path:
    current_file = Path(__file__).resolve()
    return current_file.parent.parent

# 修正後
def get_project_root() -> Path:
    # 環境変数またはconfig.jsonから取得
    config_path = os.getenv('BIRDNET_DATABASE_PATH')
    if config_path:
        return Path(config_path).parent
    else:
        # デフォルトまたは設定ファイルから読み込み
        return load_database_path_from_config()
```

#### 新しい設定方式
1. **環境変数方式**: `BIRDNET_DATABASE_PATH` で絶対パス指定
2. **設定ファイル方式**: `config.json` でデータベースパス管理
3. **起動時設定方式**: コマンドライン引数でパス指定

### 2.2 DatabaseConfig クラスの修正
```python
class DatabaseConfig:
    @staticmethod
    def get_database_path() -> str:
        # 絶対パス設定から取得
        base_path = get_configured_database_path()
        return str(base_path / "result.db")
    
    @staticmethod
    def get_alternative_paths() -> list:
        base_path = get_configured_database_path()
        return [
            base_path / "birdnet_simple.db",
            base_path / "birdnet.db", 
            base_path / "birds.db",
        ]
```

## 3. アプリケーションファイルの修正

### 3.1 db_viewer.py の修正
```python
# パス追加部分を修正
current_file = Path(__file__).resolve()
# 修正前: project_root = current_file.parent.parent
# 修正後: プロジェクトルートは設定から取得

# libパスの追加を修正
lib_path = get_lib_path()  # 設定から取得
sys.path.append(str(lib_path))
```

### 3.2 起動方式の変更
app.py の作成または db_viewer.py のリネーム検討

## 4. 起動スクリプトの修正

### 4.1 start_streamlit_viewer.bat の修正
```batch
@echo off
chcp 65001 > nul

REM データベースパスの設定
set /p DATABASE_PATH="データベースフォルダの絶対パスを入力してください: "
set BIRDNET_DATABASE_PATH=%DATABASE_PATH%

REM 既存のチェック処理...

REM Streamlit起動
streamlit run app.py
```

### 4.2 設定ファイル方式の場合
```batch
REM config.json存在チェック
if not exist "config.json" (
    echo 設定ファイルを作成してください
    echo 例: {"database_path": "C:\\path\\to\\database\\folder"}
    pause
    exit /b 1
)
```

## 5. 新しいファイル作成

### 5.1 config.json (設定ファイル方式の場合)
```json
{
    "database_path": "C:\\path\\to\\birdnet\\database",
    "audio_path": "C:\\path\\to\\birdnet\\database\\audio",
    "app_settings": {
        "port": 8501,
        "host": "localhost"
    }
}
```

### 5.2 app.py (エントリーポイント)
```python
#!/usr/bin/env python3
"""
BirdNET Streamlit Viewer - 独立版
エントリーポイント
"""

# 設定読み込み
from config import validate_configuration
import streamlit as st

def main():
    # 設定検証
    if not validate_configuration():
        st.error("設定エラー: データベースパスが正しく設定されていません")
        st.stop()
    
    # メインアプリ起動
    from db_viewer import main as viewer_main
    viewer_main()

if __name__ == "__main__":
    main()
```

### 5.3 setup_config.py (初期設定スクリプト)
```python
#!/usr/bin/env python3
"""
初期設定セットアップスクリプト
"""

import json
from pathlib import Path

def setup_configuration():
    print("BirdNET Streamlit Viewer 初期設定")
    database_path = input("データベースフォルダの絶対パスを入力: ")
    
    config = {
        "database_path": database_path,
        "audio_path": str(Path(database_path) / "audio")
    }
    
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print("設定ファイル config.json を作成しました")

if __name__ == "__main__":
    setup_configuration()
```

## 6. requirements.txt の整理

### 追加が必要な依存関係
```
# 既存の依存関係
streamlit>=1.28.0
plotly>=5.15.0
librosa==0.9.2
soundfile
numpy
pandas

# 独立リポジトリで新たに必要
pathlib2  # Python 3.4以前との互換性
python-dotenv  # 環境変数管理
```

## 7. ディレクトリ構造（新リポジトリ）

```
birdnet-streamlit-viewer/
├── README.md
├── requirements.txt
├── config.json                 # 設定ファイル（生成）
├── setup_config.py            # 初期設定スクリプト
├── start_viewer.bat           # 起動スクリプト
├── app.py                     # エントリーポイント
├── db_viewer.py              # メインアプリケーション
├── config.py                 # 設定管理（修正版）
├── utils/
│   ├── __init__.py
│   └── audio_processor.py
├── lib/                      # 依存モジュール
│   ├── db/
│   │   ├── __init__.py
│   │   └── database.py
│   └── audio_processing/
│       ├── __init__.py
│       ├── file_manager.py
│       ├── processing_manager.py
│       ├── segment_generator.py
│       └── spectrogram_generator.py
└── docs/                     # ドキュメント
    ├── CHANGELOG_GENERATION_ADDED.md
    ├── CHANGELOG_REMOVAL.md
    ├── CHANGELOG_TABLE_IMPROVEMENT.md
    ├── README_PHASE2.md
    └── README_PHASE2_VIEWER.md
```

## 8. テスト・検証項目

### 8.1 基本動作テスト
- [ ] 設定ファイル読み込み
- [ ] データベース接続
- [ ] 音声ファイル読み込み
- [ ] Streamlit起動

### 8.2 パス設定テスト
- [ ] 絶対パス設定での動作
- [ ] 異なるドライブでの動作
- [ ] 日本語パス対応

### 8.3 機能テスト
- [ ] データベース検索
- [ ] 音声セグメント再生
- [ ] スペクトログラム表示
- [ ] エクスポート機能

## 9. 移行手順

1. **新リポジトリ作成**
2. **ファイルコピー**（上記リスト参照）
3. **config.py修正**（パス設定変更）
4. **app.py作成**（エントリーポイント）
5. **起動スクリプト修正**
6. **setup_config.py作成**
7. **README.md作成**（新リポジトリ用）
8. **テスト実行**
9. **ドキュメント整備**

## 10. 注意事項

- 既存のdatabaseフォルダ構造は変更しない
- BirdNET-SQLとの互換性を維持
- Windows環境での動作を優先
- 日本語文字化け対策を忘れずに
- セキュリティ: 絶対パス設定時の権限確認

## 11. 今後の拡張予定

- 複数データベース対応
- 設定UI追加
- Docker対応
- Linux/Mac対応