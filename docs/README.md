# Twitter HTML Extractor

Twitter/X の HTML ファイルからツイートデータを抽出し、CSV ファイルに変換するツールです。

## 概要

このプロジェクトは、Twitter/X の HTML ファイルからツイートデータを抽出し、整理された形式で保存するためのツールセットです。ブラウザで手動取得した HTML ファイルから、ツイートの日時、URL、内容を抽出できます。

## 機能

- HTML ファイルからツイートデータを抽出
- 日時、ユーザー名、ツイート URL、ツイート内容、ツイート本文中の全 URL（t.co 含む）を解析
- テキストファイルと JSON ファイルに出力
- 複数ファイルのマージ機能
- CSV ファイルへの変換機能（ユーザー名カラム追加）
- ツイート抽出後、最後のツイート日時を `until:YYYY-MM-DD_HH:MM:SS_JST` 形式でコンソールに表示

## ファイル構成

```
twitter-html-extractor/
├── src/                          # ソースコード
│   ├── extract_tweets_from_html.py
│   └── merge_all_txt_to_csv.py
├── data/                         # データフォルダ
│   ├── input/                    # 入力ファイル
│   │   └── sample.html
│   └── output/                   # 出力ファイル
│       ├── txt/                  # テキストファイル
│       │   └── sample.txt
│       ├── json/                 # JSONファイル
│       │   └── sample.json
│       └── csv/                  # CSVファイル
│           └── all_tweets_sample.csv
├── docs/                         # ドキュメント
│   └── README.md
├── tests/                        # テストファイル
│   ├── test_extract_tweets.py
│   ├── test_merge_csv.py
│   └── run_tests.py
├── main.py                       # エントリーポイント
├── requirements.txt
└── .gitignore
```

## セットアップ

### 必要な環境

- Python 3.7 以上
- 必要なライブラリ：
  - beautifulsoup4
  - argparse（標準ライブラリ）
  - csv（標準ライブラリ）
  - datetime（標準ライブラリ）

### インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd twitter-html-extractor

# 必要なライブラリをインストール
pip install beautifulsoup4
```

### HTML ファイルの取得方法

1. **ブラウザでの手動取得**

   - Twitter/X のタイムラインを開く
   - F12 キーで開発者ツールを開く
   - Elements タブで HTML を確認
   - ページ全体を右クリック → 「ページのソースを表示」
   - ソースをコピーして HTML ファイルとして保存

2. **ファイル名の形式**
   - ファイル名は `YYYYMMDD.html` の形式で保存
   - 例：`250706.html`（2025 年 7 月 6 日のデータ）

## 使用方法

### 1. HTML ファイルからツイートを抽出

```bash
python main.py extract 250706
```

**出力：**

- `data/output/txt/250706.txt` - テキストファイル
- `data/output/json/250706.json` - JSON ファイル

### 2. 全ファイルをマージして CSV を作成

```bash
python main.py merge
```

**出力：**

- `data/output/csv/all_tweets.csv` - 全ツイートの統合 CSV ファイル

### 3. 直接スクリプトを実行（従来の方法）

```bash
# ツイート抽出
python src/extract_tweets_from_html.py 250706

# マージ実行
python src/merge_all_txt_to_csv.py
```

## ファイル形式

### 入力ファイル

- HTML ファイル（ブラウザで手動取得した Twitter/X のページソース）
- ファイル名形式：`YYYYMMDD.html`（例：`250706.html`）

### 出力ファイル

#### テキストファイル（.txt）

```
抽出日時: 2025-01-27 15:30:00
抽出ツイート数: 8
==================================================
1.
ユーザー名: サンプルユーザー
日時: 2025/06/15 12:44:35
ツイートURL: https://x.com/username/status/1234567890123456789
ツイート内容... https://t.co/xxxx https://example.com/...
------------------------------
```

#### JSON ファイル（.json）

```json
{
  "extraction_time": "2025-01-27T15:30:00",
  "tweet_count": 8,
  "tweets": [
    {
      "id": 1,
      "user_name": "サンプルユーザー",
      "text": "ツイート内容... https://t.co/xxxx https://example.com/...",
      "datetime": "2025/06/15 12:44:35",
      "quote_url": "https://x.com/...",
      "raw_html": "..."
    }
  ]
}
```

#### CSV ファイル（.csv）

```csv
ユーザー名,日時,URL,ツイート内容,元ファイル
サンプルユーザー,2025/06/15 12:44:35,https://x.com/username/status/1234567890123456789,"ツイート内容... https://t.co/xxxx https://example.com/...",250706.txt
```

## 注意事項

- 入力 HTML ファイルは`data/input`フォルダに配置してください
- 出力ファイルは`data/output`フォルダに自動生成されます
- 日時は JST（日本標準時）で表示されます
- ツイートの重複は排除されません（元の HTML の構造に依存）

## トラブルシューティング

### よくある問題

1. **ファイルが見つからないエラー**

   - `data/input`フォルダが存在することを確認
   - HTML ファイルが正しい形式で配置されていることを確認

2. **抽出件数が少ない**

   - HTML ファイルの構造を確認
   - セレクタが適切に動作しているか確認

3. **日時が正しく表示されない**
   - HTML ファイルの`datetime`属性を確認
   - タイムゾーン変換が正しく動作しているか確認

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 更新履歴

- v1.0.0: 初期リリース
  - HTML ファイルからのツイート抽出機能
  - テキスト・JSON 出力機能
  - CSV 変換機能
  - マージ機能
