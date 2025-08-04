#!/usr/bin/env python3
"""
BirdNET Streamlit Viewer - 独立版
エントリーポイント
"""

import sys
from pathlib import Path

# 必要なパスを追加
current_file = Path(__file__).resolve()
project_root = current_file.parent

# libパスとstreamlit_viewerパスを追加
lib_path = project_root / "lib"
streamlit_viewer_path = project_root / "streamlit_viewer"
sys.path.insert(0, str(lib_path))
sys.path.insert(0, str(project_root))

# 設定読み込み
from config import validate_configuration, get_lib_path
import streamlit as st

def main():
    """メインアプリケーション"""
    
    # 設定検証
    if not validate_configuration():
        st.error("❌ 設定エラー: データベースパスが正しく設定されていません")
        
        st.markdown("### 🔧 設定方法")
        st.markdown("以下のいずれかの方法で設定を行ってください：")
        
        st.markdown("#### 1. 環境変数による設定")
        st.code("set BIRDNET_DATABASE_PATH=C:\\path\\to\\database\\folder")
        
        st.markdown("#### 2. 設定ファイルによる設定")
        st.markdown("setup_config.py を実行して設定ファイルを作成してください：")
        st.code("python setup_config.py")
        
        st.markdown("#### 3. 手動で config.json を作成")
        st.code('''{
    "database_path": "C:\\\\path\\\\to\\\\database\\\\folder",
    "audio_path": "C:\\\\path\\\\to\\\\database\\\\folder\\\\audio"
}''')
        
        st.stop()
    
    # 設定が正常な場合、メインアプリを起動
    try:
        # db_viewer.pyファイルのパス
        db_viewer_path = project_root / "streamlit_viewer" / "db_viewer.py"
        
        if not db_viewer_path.exists():
            st.error("❌ streamlit_viewer/db_viewer.py が見つかりません。")
            st.stop()
        
        # db_viewer.pyの内容を読み込んで実行
        with open(db_viewer_path, 'r', encoding='utf-8') as f:
            db_viewer_code = f.read()
        
        # グローバル名前空間で実行
        exec(db_viewer_code, globals())
            
    except Exception as e:
        st.error(f"❌ アプリケーション起動エラー: {e}")
        st.markdown(f"詳細: {str(e)}")
        st.stop()

if __name__ == "__main__":
    main()