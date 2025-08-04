"""
BirdNet DB Viewer 設定ファイル（独立版）
パス設定やアプリケーション設定を管理
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# プロジェクトルートパス（独立版用）
def get_project_root() -> Path:
    """プロジェクトルートディレクトリを取得（環境変数またはconfig.jsonから）"""
    # 環境変数から取得
    config_path = os.getenv('BIRDNET_DATABASE_PATH')
    if config_path:
        return Path(config_path).parent
    else:
        # 設定ファイルから読み込み
        return load_database_path_from_config()

def load_database_path_from_config() -> Path:
    """config.jsonから設定を読み込み"""
    config_file = Path(__file__).parent / "config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                database_path = config.get('database_path')
                if database_path:
                    return Path(database_path)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"設定ファイル読み込みエラー: {e}")
    
    # デフォルトまたはエラー時は現在のディレクトリを返す
    return Path(__file__).resolve().parent

def get_configured_database_path() -> Path:
    """設定されたデータベースフォルダのパスを取得"""
    # 環境変数から取得
    db_path = os.getenv('BIRDNET_DATABASE_PATH')
    if db_path:
        return Path(db_path)
    
    # 設定ファイルから取得
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                database_path = config.get('database_path')
                if database_path:
                    return Path(database_path)
        except (json.JSONDecodeError, KeyError) as e:
            print(f"設定ファイル読み込みエラー: {e}")
    
    # デフォルト値（現在のディレクトリのdatabaseフォルダ）
    return Path(__file__).resolve().parent / "database"

def get_lib_path() -> Path:
    """libディレクトリのパスを取得"""
    return Path(__file__).resolve().parent / "lib"

def validate_configuration() -> bool:
    """設定が正しいかチェック"""
    try:
        db_path = get_configured_database_path()
        if not db_path.exists():
            print(f"データベースフォルダが見つかりません: {db_path}")
            return False
        
        # データベースファイルの存在チェック
        db_config = DatabaseConfig()
        main_db = Path(db_config.get_database_path())
        alt_paths = [Path(p) for p in db_config.get_alternative_paths()]
        
        if not main_db.exists() and not any(p.exists() for p in alt_paths):
            print("データベースファイルが見つかりません")
            return False
        
        return True
    except Exception as e:
        print(f"設定検証エラー: {e}")
        return False

# データベース設定
class DatabaseConfig:
    """データベース関連の設定"""
    
    @staticmethod
    def get_database_path() -> str:
        """データベースファイルのパスを取得"""
        db_folder = get_configured_database_path()
        return str(db_folder / "result.db")
    
    @staticmethod
    def get_alternative_paths() -> list:
        """代替データベースパスのリスト"""
        db_folder = get_configured_database_path()
        return [
            str(db_folder / "birdnet_simple.db"),
            str(db_folder / "birdnet.db"), 
            str(db_folder / "birds.db"),
        ]

# 音声ファイル設定
class AudioConfig:
    """音声ファイル関連の設定"""
    
    @staticmethod
    def get_audio_base_path() -> Path:
        """音声ファイルのベースパスを取得"""
        db_folder = get_configured_database_path()
        
        # 設定ファイルから音声パスを取得
        config_file = Path(__file__).parent / "config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    audio_path = config.get('audio_path')
                    if audio_path:
                        return Path(audio_path)
            except (json.JSONDecodeError, KeyError):
                pass
        
        # デフォルトはdatabaseフォルダ内のaudioフォルダ
        return db_folder / "audio"
    
    @staticmethod
    def get_supported_formats() -> list:
        """サポートされている音声フォーマット"""
        return ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']

# アプリケーション設定
class AppConfig:
    """アプリケーション全体の設定"""
    
    # ページ設定
    PAGE_TITLE = "BirdNet DB ビューワー（独立版）"
    PAGE_ICON = "🐦"
    LAYOUT = "wide"
    
    # デフォルト値
    DEFAULT_LIMIT_OPTIONS = [10, 50, 100, 500, 1000]
    MAX_DISPLAY_RECORDS = 10000
    DEFAULT_CONFIDENCE_MIN = 0.0
    
    # UI設定
    ITEMS_PER_PAGE = 10
    
    @staticmethod
    def get_custom_css() -> str:
        """カスタムCSSを取得"""
        return """
        <style>
        /* メインコンテナ */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        /* サイドバー */
        .css-1d391kg {
            background-color: #f8f9fa;
        }

        /* 検索コンテナ */
        .search-container {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
        }

        /* 結果カード */
        .result-card {
            background: white;
            padding: 1rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 0.5rem 0;
            border-left: 4px solid #4CAF50;
        }

        /* 音声プレイヤー */
        .audio-player {
            background: #f0f2f6;
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }

        /* カードスタイル */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }

        /* ステータスアイコン */
        .status-ok { color: #28a745; }
        .status-error { color: #dc3545; }
        .status-warning { color: #ffc107; }

        /* ヘッダー */
        .header {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
        """

# 検索・フィルタ設定
class SearchConfig:
    """検索とフィルタの設定"""
    
    # 検索可能カラム
    SEARCHABLE_COLUMNS = {
        'session_name': 'セッション名',
        'filename': 'ファイル名', 
        'scientific_name': '学名',
        'common_name': '和名'
    }
    
    # フィルタ可能カラム
    FILTERABLE_COLUMNS = {
        'confidence': '信頼度',
        'analysis_date': '解析日',
        'created_at': '作成日時'
    }
    
    # ソート可能カラム
    SORTABLE_COLUMNS = {
        'confidence': '信頼度',
        'created_at': '作成日時',
        'common_name': '種名',
        'session_name': 'セッション'
    }

# エクスポート設定
class ExportConfig:
    """データエクスポートの設定"""
    
    @staticmethod
    def get_csv_filename() -> str:
        """CSVファイル名を生成"""
        from datetime import datetime
        return f"birdnet_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    @staticmethod
    def get_json_filename() -> str:
        """JSONファイル名を生成"""
        from datetime import datetime
        return f"birdnet_search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

# 全設定をまとめる
def get_all_config() -> Dict[str, Any]:
    """全設定を辞書形式で取得"""
    return {
        'database': DatabaseConfig,
        'audio': AudioConfig,
        'app': AppConfig,
        'search': SearchConfig,
        'export': ExportConfig,
        'project_root': get_project_root()
    }