#!/usr/bin/env python3
"""
BirdNET Streamlit Viewer 初期設定セットアップスクリプト
データベースパスを設定してconfig.jsonを作成します
"""

import json
import os
from pathlib import Path

def validate_database_path(path_str: str) -> bool:
    """データベースパスが有効かチェック"""
    try:
        path = Path(path_str)
        if not path.exists():
            print(f"⚠️  パスが存在しません: {path}")
            return False
        
        if not path.is_dir():
            print(f"⚠️  パスがディレクトリではありません: {path}")
            return False
        
        # データベースファイルの存在チェック
        db_files = [
            "result.db",
            "birdnet_simple.db", 
            "birdnet.db",
            "birds.db"
        ]
        
        found_db = False
        for db_file in db_files:
            if (path / db_file).exists():
                print(f"✅ データベースファイルを発見: {db_file}")
                found_db = True
                break
        
        if not found_db:
            print("⚠️  データベースファイルが見つかりません")
            print(f"   以下のファイルのいずれかが必要です: {', '.join(db_files)}")
            create_anyway = input("それでも設定を作成しますか？ (y/N): ").lower().strip()
            return create_anyway == 'y'
        
        return True
        
    except Exception as e:
        print(f"❌ パス検証エラー: {e}")
        return False

def setup_configuration():
    """設定ファイルのセットアップ"""
    print("=" * 60)
    print("🐦 BirdNET Streamlit Viewer 初期設定")
    print("=" * 60)
    print()
    
    # 既存の設定ファイルをチェック
    config_file = Path("config.json")
    if config_file.exists():
        print("⚠️  既存の設定ファイルが見つかりました")
        overwrite = input("上書きしますか？ (y/N): ").lower().strip()
        if overwrite != 'y':
            print("設定をキャンセルしました")
            return
    
    print("📁 データベースフォルダの設定")
    print("   BirdNETのデータベースファイル（result.db等）があるフォルダを指定してください")
    print()
    
    while True:
        database_path = input("データベースフォルダの絶対パスを入力: ").strip()
        
        if not database_path:
            print("❌ パスを入力してください")
            continue
        
        # クォートを除去
        database_path = database_path.strip('"').strip("'")
        
        # パスの正規化
        database_path = os.path.expanduser(database_path)
        database_path = os.path.abspath(database_path)
        
        print(f"🔍 パスを検証中: {database_path}")
        
        if validate_database_path(database_path):
            break
        
        retry = input("別のパスを試しますか？ (Y/n): ").lower().strip()
        if retry == 'n':
            print("設定をキャンセルしました")
            return
    
    # 音声フォルダの設定
    print()
    print("🎵 音声フォルダの設定")
    default_audio_path = str(Path(database_path) / "audio")
    print(f"   デフォルト: {default_audio_path}")
    
    audio_path = input(f"音声フォルダのパス (Enter でデフォルト): ").strip()
    if not audio_path:
        audio_path = default_audio_path
    else:
        # クォートを除去
        audio_path = audio_path.strip('"').strip("'")
        audio_path = os.path.expanduser(audio_path)
        audio_path = os.path.abspath(audio_path)
    
    # アプリケーション設定
    print()
    print("⚙️  アプリケーション設定")
    
    port = input("ポート番号 (デフォルト: 8501): ").strip()
    if not port:
        port = 8501
    else:
        try:
            port = int(port)
        except ValueError:
            print("⚠️  無効なポート番号、デフォルト値を使用します")
            port = 8501
    
    host = input("ホスト (デフォルト: localhost): ").strip()
    if not host:
        host = "localhost"
    
    # 設定辞書を作成
    config = {
        "database_path": database_path,
        "audio_path": audio_path,
        "app_settings": {
            "port": port,
            "host": host
        },
        "created_at": str(Path(__file__).parent.absolute()),
        "version": "1.0.0"
    }
    
    # config.jsonに保存
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print()
        print("✅ 設定ファイル config.json を作成しました")
        print()
        print("📄 設定内容:")
        print(f"   データベース: {database_path}")
        print(f"   音声フォルダ: {audio_path}")
        print(f"   ホスト:ポート: {host}:{port}")
        print()
        print("🚀 アプリケーションを起動するには:")
        print("   python app.py")
        print("   または")
        print("   streamlit run app.py")
        
    except Exception as e:
        print(f"❌ 設定ファイル作成エラー: {e}")
        return
    
    print()
    print("=" * 60)
    print("設定完了！")
    print("=" * 60)

def show_current_config():
    """現在の設定を表示"""
    config_file = Path("config.json")
    if not config_file.exists():
        print("❌ 設定ファイルが見つかりません")
        return
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("📄 現在の設定:")
        print(f"   データベース: {config.get('database_path', 'N/A')}")
        print(f"   音声フォルダ: {config.get('audio_path', 'N/A')}")
        
        app_settings = config.get('app_settings', {})
        print(f"   ホスト:ポート: {app_settings.get('host', 'N/A')}:{app_settings.get('port', 'N/A')}")
        
    except Exception as e:
        print(f"❌ 設定ファイル読み込みエラー: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--show":
        show_current_config()
    else:
        setup_configuration()