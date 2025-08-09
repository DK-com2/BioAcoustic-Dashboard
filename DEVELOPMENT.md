# 開発者向けガイド

このドキュメントでは、BioAcoustic Dashboardの開発・カスタマイズ・拡張について説明します。

## アーキテクチャ概要

### システム構成

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend        │    │   Data Layer    │
│   (Streamlit)   │◄──►│   (Python)       │◄──►│   (SQLite)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
│                      │                      │
├─ db_viewer.py        ├─ audio_processing/   ├─ result.db
├─ pages/              ├─ db/                 ├─ audio_segments/
└─ utils/              └─ config.py          └─ spectrograms/
```

### モジュール構成

- **streamlit_viewer/**: UI層（Streamlitアプリケーション）
- **lib/audio_processing/**: 音声処理ロジック
- **lib/db/**: データベース操作レイヤー
- **config.py**: 設定管理
- **app.py**: アプリケーションエントリーポイント

## ディレクトリ詳細

### /streamlit_viewer/

```
streamlit_viewer/
├── db_viewer.py           # メインビューワー（単一ページアプリ）
├── pages/                 # マルチページ機能（将来の拡張用）
│   ├── __init__.py
│   ├── analytics.py       # 統計・分析ページ
│   └── settings.py        # 設定ページ  
└── utils/                 # UI共通ユーティリティ
    ├── __init__.py
    └── audio_processor.py  # 音声処理UI補助
```

### /lib/audio_processing/

```
audio_processing/
├── __init__.py
├── processing_manager.py   # 統合処理マネージャー
├── segment_generator.py    # 音声セグメント生成
├── spectrogram_generator.py # スペクトログラム生成  
└── file_manager.py        # ファイル管理（パス解決等）
```

### /lib/db/

```
db/
├── __init__.py
├── database.py           # データベース操作クラス
└── session_manager.py    # セッション管理
```

## 主要コンポーネント

### 1. BirdNetSimpleDB (lib/db/database.py)

データベース操作の中核クラス：

```python
class BirdNetSimpleDB:
    def __init__(self, db_path: str)
    
    # データ取得
    def get_detections_by_session(self, session_name: str) -> List[Dict]
    def get_detections_by_species(self, species: str) -> List[Dict]  
    def get_detections_by_confidence(self, min_confidence: float) -> List[Dict]
    
    # データ更新
    def update_quality_status(self, detection_id: int, status: str) -> bool
    
    # 統計情報
    def get_session_summary(self) -> Dict
    def get_species_summary(self) -> Dict
```

### 2. ProcessingManager (lib/audio_processing/processing_manager.py)

音声・画像ファイルの生成管理：

```python
class ProcessingManager:
    def __init__(self, db_path: str, enable_spectrogram: bool = True)
    
    # 単一検出の処理
    def process_single_detection(self, detection_id: int) -> Tuple[bool, str]
    
    # バッチ処理  
    def process_multiple_detections(self, detection_ids: List[int]) -> Dict
    
    # ファイル存在確認
    def check_files_exist(self, detection_id: int) -> Dict[str, bool]
```

### 3. Streamlit UI Components

#### データテーブル (show_data_view関数)
```python
def show_data_view():
    """メインのデータ表示機能"""
    # フィルタリング
    # データ取得
    # テーブル表示 
    # 選択処理
    # プレビュー表示
```

#### プレビューエリア (show_preview_area関数)
```python
def show_preview_area(selected_record):
    """選択されたレコードのプレビュー"""
    # 音声プレイヤー
    # スペクトログラム表示
    # 品質評価ボタン
    # ファイル生成ボタン
```

## 開発環境セットアップ

### 開発用依存関係

```bash
# 開発ツールのインストール
pip install -e .  # エディタブルインストール
pip install pytest pytest-cov black flake8 mypy jupyter

# pre-commit フック（オプション）
pip install pre-commit
pre-commit install
```

### VS Code 設定

`.vscode/settings.json`:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=100"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/.pytest_cache": true
    }
}
```

## テスト

### テスト構造

```
tests/
├── __init__.py
├── conftest.py              # pytest設定・フィクスチャ  
├── test_database.py         # データベース操作テスト
├── test_audio_processing.py # 音声処理テスト
├── test_config.py           # 設定管理テスト
└── integration/             # 統合テスト
    ├── test_full_workflow.py
    └── test_ui_components.py
```

### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=lib --cov=streamlit_viewer

# 特定テストのみ
pytest tests/test_database.py -v

# マーク付きテスト
pytest -m "not slow"
```

### サンプルテスト

```python
# tests/test_database.py
import pytest
from lib.db.database import BirdNetSimpleDB

@pytest.fixture
def sample_db():
    """テスト用データベース"""
    db = BirdNetSimpleDB(":memory:")
    # テストデータ投入
    return db

def test_get_detections_by_session(sample_db):
    """セッション別取得のテスト"""
    detections = sample_db.get_detections_by_session("test_session")
    assert len(detections) > 0
    assert all(d['session_name'] == "test_session" for d in detections)
```

## UI カスタマイズ

### カスタムCSS

`db_viewer.py` 内でCSS定義：

```python
st.markdown("""
<style>
.custom-metric {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
}

.preview-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #667eea;
}
</style>
""", unsafe_allow_html=True)
```

### コンポーネントの拡張

新しいページを追加：

```python
# streamlit_viewer/pages/analytics.py
import streamlit as st
import plotly.express as px

def show_analytics_page():
    st.title("分析ダッシュボード")
    
    # 種別分布チャート
    species_data = get_species_distribution()
    fig = px.pie(species_data, values='count', names='species')
    st.plotly_chart(fig)
    
    # 時系列分析
    temporal_data = get_temporal_distribution()  
    fig = px.line(temporal_data, x='date', y='detections')
    st.plotly_chart(fig)
```

## プラグイン・拡張

### 新しい音声処理機能

```python
# lib/audio_processing/custom_processor.py
class CustomAudioProcessor:
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
        
    def apply_noise_reduction(self, audio_data: np.ndarray) -> np.ndarray:
        """ノイズリダクション処理"""
        # 実装
        return processed_audio
        
    def extract_features(self, audio_data: np.ndarray) -> Dict:
        """特徴量抽出"""
        features = {
            'mfcc': librosa.feature.mfcc(audio_data, sr=self.sample_rate),
            'spectral_centroid': librosa.feature.spectral_centroid(audio_data, sr=self.sample_rate),
            # その他の特徴量
        }
        return features
```

### データベース拡張

```python
# lib/db/extended_database.py  
class ExtendedBirdNetDB(BirdNetSimpleDB):
    def add_user_annotations(self, detection_id: int, annotation: Dict) -> bool:
        """ユーザーアノテーション追加"""
        # 実装
        
    def get_detection_statistics(self) -> Dict:
        """高度な統計情報"""
        # 実装
        
    def export_to_format(self, format_type: str) -> str:
        """他フォーマットへのエクスポート"""
        # CSV, JSON, XML等への変換
```

## パフォーマンス最適化

### データベース最適化

```sql
-- インデックス作成
CREATE INDEX idx_session_name ON bird_detections(session_name);
CREATE INDEX idx_common_name ON bird_detections(common_name);
CREATE INDEX idx_confidence ON bird_detections(confidence);
CREATE INDEX idx_created_at ON bird_detections(created_at);
```

### Streamlitキャッシュ活用

```python
@st.cache_data(ttl=3600)  # 1時間キャッシュ
def get_heavy_computation_result(param):
    """重い計算結果をキャッシュ"""
    # 時間のかかる処理
    return result

@st.cache_resource  # リソース系（DB接続等）
def get_database_connection():
    """データベース接続をキャッシュ"""
    return BirdNetSimpleDB(db_path)
```

### 非同期処理

```python
import asyncio
import aiofiles

async def process_audio_async(detection_ids: List[int]):
    """非同期での音声処理"""
    tasks = []
    for detection_id in detection_ids:
        task = asyncio.create_task(process_single_audio(detection_id))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results
```

## デプロイメント

### Docker化

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# システム依存関係
RUN apt-get update && apt-get install -y \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーション
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  birdnet-dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./database:/app/database
      - ./config.json:/app/config.json
    environment:
      - STREAMLIT_SERVER_ADDRESS=0.0.0.0
      - STREAMLIT_SERVER_PORT=8501
```

### Heroku デプロイ

```bash
# Heroku CLI インストール後
heroku create your-app-name
heroku buildpacks:set heroku/python
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

# 設定
heroku config:set BIRDNET_DATABASE_PATH=/app/database

# デプロイ
git push heroku main
```

## デバッグ・ログ

### ログ設定

```python
# lib/utils/logger.py
import logging
import streamlit as st

def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# 使用例
logger = setup_logger(__name__)
logger.info("Processing started")
```

### Streamlit デバッグ

```python
# デバッグ情報表示
if st.sidebar.checkbox("Debug Mode"):
    st.subheader("Debug Information")
    st.write("Session State:", st.session_state)
    st.write("Selected Record:", st.session_state.get('selected_record'))
    
    # 処理時間計測
    import time
    start_time = time.time()
    # 処理
    end_time = time.time()
    st.write(f"Processing Time: {end_time - start_time:.2f}s")
```

## コントリビューション・コーディング規約

### コードスタイル

- **フォーマッタ**: Black (line-length=100)
- **リンター**: flake8, mypy
- **docstring**: Google Style

```python
def process_audio_segment(
    detection_id: int, 
    output_dir: Path, 
    sample_rate: int = 22050
) -> Tuple[bool, str]:
    """音声セグメントを処理する.
    
    Args:
        detection_id: 検出ID
        output_dir: 出力ディレクトリ
        sample_rate: サンプリングレート
        
    Returns:
        Tuple[bool, str]: (成功フラグ, メッセージ)
        
    Raises:
        FileNotFoundError: 音声ファイルが見つからない場合
        ValueError: 不正なパラメータの場合
    """
```

### Git ワークフロー

1. **Feature Branch**: `feature/feature-name`
2. **Bug Fix**: `bugfix/issue-description`  
3. **Hot Fix**: `hotfix/urgent-fix`

```bash
# 機能開発
git checkout -b feature/add-export-functionality
git commit -m "feat: add CSV export with custom columns"
git push origin feature/add-export-functionality
# プルリクエスト作成
```

### コミットメッセージ

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: 新機能
- `fix`: バグ修正  
- `docs`: ドキュメント
- `style`: フォーマット
- `refactor`: リファクタリング
- `test`: テスト追加
- `chore`: その他

---

このガイドを参考に、BioAcoustic Dashboardの開発・拡張を行ってください。質問や提案がある場合は、Issueまたはプルリクエストで お知らせください。