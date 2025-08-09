# BioAcoustic Dashboard

BirdNETの解析結果を視覚的に確認・管理するためのStreamlitダッシュボードアプリケーションです。

## 主な機能

- **検索・フィルタリング**: セッション名、種名、信頼度、品質評価による絞り込み
- **音声プレビュー**: 検出された鳥の音声セグメントをブラウザで再生
- **スペクトログラム表示**: 音声の可視化による詳細確認
- **品質評価システム**: 検出結果を承認・却下・保留で管理
- **ファイル生成**: 音声セグメントとスペクトログラムの自動生成
- **テーブル表示**: ID付きでトレースしやすいデータ表示
- **エクスポート機能**: 検索結果をCSVで出力

## 重要な特徴

### データベースの柔軟な配置

**このアプリケーションはデータベースをリポジトリ内に置く必要がありません。**

- BirdNETで生成した既存のデータベース（任意の場所）をそのまま使用可能
- データベースパスは設定ファイルまたは環境変数で指定
- 複数のプロジェクトや場所のデータベースを簡単に切り替え可能
- データベースファイルをコピーしたり移動したりする必要なし

**配置例:**
```
# あなたのBirdNETプロジェクト
/your/birdnet/project/
├── result.db              ← 既存のデータベース
├── audio/                 ← 既存の音声ファイル
└── analysis_results/

# このダッシュボードアプリ
/separate/location/BioAcoustic-Dashboard/
├── app.py
├── config.json           ← データベースパスを指定
└── streamlit_viewer/
```

設定ファイル（config.json）でパスを指定するだけで接続完了：
```json
{
  "database_path": "/your/birdnet/project",
  "audio_path": "/your/birdnet/project/audio"
}
```

## クイックスタート

### 1. 環境構築

#### 必要な環境
- Python 3.9以上
- Windows、macOS、Linux対応

#### インストール手順

1. **リポジトリのクローン**
   ```bash
   git clone <repository-url>
   cd BioAcoustic-Dashboard
   ```

2. **仮想環境の作成と有効化**
   ```bash
   # Windows
   python -m venv venv
   venv\\Scripts\\activate
   
   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **依存パッケージのインストール**
   ```bash
   pip install -r requirements.txt
   ```

### 2. 設定

#### 設定スクリプトの実行（推奨）
```bash
python setup_config.py
```

このスクリプトが以下を自動設定します：
- データベースパスの検証
- 音声フォルダの設定
- アプリケーション設定（ホスト・ポート）

#### 手動設定
`config.json`を作成して以下の内容を設定：

```json
{
  "database_path": "C:\\path\\to\\database\\folder",
  "audio_path": "C:\\path\\to\\database\\folder\\audio",
  "app_settings": {
    "port": 8501,
    "host": "localhost"
  },
  "version": "1.0.0"
}
```

#### 環境変数による設定
```bash
# Windows
set BIRDNET_DATABASE_PATH=C:\\path\\to\\database\\folder

# macOS/Linux  
export BIRDNET_DATABASE_PATH=/path/to/database/folder
```

### 3. 起動

```bash
python app.py
```

または

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` にアクセス

## プロジェクト構造

```
BioAcoustic-Dashboard/
├── app.py                      # メインエントリーポイント
├── config.py                   # 設定管理モジュール
├── config.json                 # 設定ファイル
├── setup_config.py            # 初期設定スクリプト
├── requirements.txt           # Python依存パッケージ
├── start_viewer.bat           # Windows用起動スクリプト
│
├── streamlit_viewer/          # Streamlitアプリケーション
│   ├── db_viewer.py          # メインビューワー
│   ├── pages/                # 追加ページ（将来の拡張用）
│   └── utils/                # ユーティリティ
│       ├── __init__.py
│       └── audio_processor.py
│
├── lib/                       # コアライブラリ
│   ├── audio_processing/      # 音声処理モジュール
│   │   ├── __init__.py
│   │   ├── processing_manager.py
│   │   ├── segment_generator.py
│   │   ├── spectrogram_generator.py
│   │   └── file_manager.py
│   └── db/                    # データベース操作
│       ├── __init__.py
│       ├── database.py
│       └── session_manager.py
│
└── database/                  # データベースとファイル
    ├── result.db             # BirdNET解析結果DB
    ├── audio/               # 元音声ファイル
    │   ├── inbox/          # 処理待ち音声
    │   ├── completed/      # 処理済み音声
    │   └── failed/         # 処理失敗音声
    ├── audio_segments/      # 生成された音声セグメント
    └── spectrograms/        # 生成されたスペクトログラム画像
```

## データベース構造

### bird_detections テーブル

BirdNETの解析結果を格納するメインテーブル：

| カラム名 | 型 | 制約 | 説明 |
|----------|----|----- |------|
| **id** | INTEGER | PRIMARY KEY | ユニークな検出ID |
| **session_name** | TEXT | NOT NULL | 解析セッション名 |
| **model_name** | TEXT | NULL | 使用したBirdNETモデル名 |
| **model_type** | TEXT | NULL | モデルの種類 |
| **filename** | TEXT | NOT NULL | 元音声ファイル名 |
| **file_path** | TEXT | NULL | 元音声ファイルのパス |
| **start_time_seconds** | REAL | NOT NULL | 検出開始時間（秒） |
| **end_time_seconds** | REAL | NOT NULL | 検出終了時間（秒） |
| **scientific_name** | TEXT | NULL | 学名 |
| **common_name** | TEXT | NULL | 一般名（日本語名など） |
| **confidence** | REAL | NOT NULL | 信頼度（0.0-1.0） |
| **location** | TEXT | NULL | 録音場所 |
| **species** | TEXT | NULL | 種名（追加情報） |
| **analysis_date** | TEXT | NULL | 解析実行日 |
| **created_at** | TIMESTAMP | NULL | レコード作成日時 |

### 品質評価システム（拡張機能）

アプリケーションが自動的に以下のカラムを追加します：

| カラム名 | 型 | 制約 | 説明 |
|----------|----|----- |------|
| **quality_status** | TEXT | DEFAULT 'pending' | 品質評価状態 |
| **reviewed_at** | TIMESTAMP | NULL | レビュー実行日時 |

**quality_status** の値：
- `pending`: 評価待ち（デフォルト）
- `approved`: 承認済み
- `rejected`: 却下

## 使用方法

### 基本操作

1. **データの検索**
   - サイドバーで検索条件を設定
   - セッション名、種名、信頀度、品質評価でフィルタリング
   - 検索実行ボタンでデータを取得

2. **行の選択と詳細表示**
   - テーブルの行をクリックして選択
   - 選択した行の詳細が下部のプレビューエリアに表示
   - IDカラムで選択行をトレース可能

3. **音声・スペクトログラムの確認**
   - プレビューエリアで音声再生
   - スペクトログラム画像の表示
   - ダウンロードボタンでファイルを保存

4. **品質評価**
   - 承認、却下、保留ボタンで評価
   - 評価状態がテーブルに反映
   - フィルタリングで評価済み・未評価を絞り込み

5. **ファイル生成**
   - 音声、画像、両方ボタンでファイル生成
   - 既存ファイルがある場合は上書きアイコンで表示
   - 生成状況はテーブルのチェックマークで確認

6. **データエクスポート**
   - CSVダウンロードボタンで検索結果をエクスポート
   - ファイル名に日時が自動付与

### 複数データベースの切り替え

異なるBirdNETプロジェクトを切り替える場合：

1. **設定ファイルを編集**
   ```bash
   # config.jsonのdatabase_pathを変更
   {
     "database_path": "/path/to/another/project",
     "audio_path": "/path/to/another/project/audio"
   }
   ```

2. **環境変数で一時切り替え**
   ```bash
   # Windows
   set BIRDNET_DATABASE_PATH=D:\Other_Project\database
   python app.py
   
   # macOS/Linux  
   export BIRDNET_DATABASE_PATH=/path/to/other/project
   python app.py
   ```

3. **複数設定ファイル管理**
   ```bash
   # プロジェクト別設定ファイル
   config_forest_study.json
   config_urban_birds.json
   config_migration_2024.json
   
   # 使用時にコピーまたはシンボリックリンク
   cp config_forest_study.json config.json
   ```

### 詳細機能

詳しい使用方法については以下のドキュメントを参照：

- [セットアップガイド](SETUP.md)
- [開発者向けガイド](DEVELOPMENT.md)
- [トラブルシューティング](TROUBLESHOOTING.md)

## トラブルシューティング

### よくある問題

**1. 起動時に設定エラーが表示される**
```
設定エラー: データベースパスが正しく設定されていません
```
→ `python setup_config.py` で設定を作成してください

**2. ライブラリの警告が表示される**
```
librosa.util.files.py: UserWarning: pkg_resources is deprecated
```
→ `pip install --upgrade librosa` でライブラリを更新してください

**3. 音声ファイルが再生できない**
- 音声ファイルの形式を確認（WAV推奨）
- ファイルパスの設定を確認
- ブラウザの音声再生機能を確認

**4. スペクトログラムが表示されない**
- matplotlib、librosaの正常インストールを確認
- ファイル生成ボタンでスペクトログラムを再生成

## 依存パッケージ

主要な依存関係：

- **streamlit** (>=1.28.0): Webアプリケーションフレームワーク
- **pandas** (>=1.5.0): データ処理
- **librosa** (>=0.11.0): 音声処理・解析
- **matplotlib** (>=3.6.0): グラフ・画像生成
- **plotly** (>=5.15.0): インタラクティブグラフ
- **streamlit-aggrid** (>=1.1.0): 高機能テーブル表示

完全な依存関係は `requirements.txt` を参照してください。

## コントリビューション

1. このリポジトリをフォーク
2. フィーチャーブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成


## 変更履歴

- **v1.0.0** (2025-01): 初回リリース
  - 基本的な検索・表示機能
  - 音声・スペクトログラム生成
  - 品質評価システム
  - ID付きテーブル表示

---

## サポート

問題や質問がある場合：

1. [Issues](../../issues) で既存の問題を検索
2. 新しいIssueを作成
3. 詳細な環境情報と再現手順を記載

---

**Happy Bird Watching!**