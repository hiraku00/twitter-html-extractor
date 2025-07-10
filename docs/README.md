# Twitter HTML Extractor

Twitter/X の HTML ファイルからツイートデータを抽出し、CSV ファイルに変換するツールです。

## 概要

このプロジェクトは、Twitter/X の HTML ファイルからツイートデータを抽出し、整理された形式で保存するためのツールセットです。ブラウザで取得した HTML 要素をクリップボード経由で保存し、ツイートの日時、URL、内容を抽出できます。

## 機能

- HTML ファイルからツイートデータを抽出
- 日時、ユーザー名、ツイート URL、ツイート内容、ツイート本文中の全 URL（t.co 含む）を解析
- テキストファイルと JSON ファイルに出力
- 複数ファイルのマージ機能
- CSV ファイルへの変換機能（ユーザー名カラム追加）
- ツイート抽出後、最後のツイート日時を `until:YYYY-MM-DD_HH:MM:SS_JST` 形式でコンソールに表示
- **until 日付をクリップボードに自動コピー（次回の検索条件としてすぐ貼り付けできるようにするため）**
- **クリップボードの内容から HTML ファイルを作成する機能（手動でファイルを配置する必要なし）**
- **Twitter の HTML ファイル作成を自動化する機能（pyautogui 使用）**

## ファイル構成

```
twitter-html-extractor/
├── src/                          # ソースコード
│   ├── extract_tweets_from_html.py
│   ├── merge_all_txt_to_csv.py
│   └── create_twitter_html_auto.py
├── data/                         # データフォルダ
│   ├── input/                    # 入力ファイル（スクリプトで自動生成）
│   └── output/                   # 出力ファイル
│       ├── txt/                  # テキストファイル
│       ├── json/                 # JSONファイル
│       └── csv/                  # CSVファイル
├── docs/                         # ドキュメント
│   └── README.md
├── tests/                        # テストファイル
│   ├── test_extract_tweets.py
│   ├── test_merge_csv.py
│   ├── test_create_html.py
│   ├── test_create_twitter_html_auto.py
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
  - pyperclip
  - pyautogui（自動化機能用）
  - argparse（標準ライブラリ）
  - csv（標準ライブラリ）
  - datetime（標準ライブラリ）

### インストール

```bash
# リポジトリをクローン
git clone <repository-url>
cd twitter-html-extractor

# 必要なライブラリをインストール
pip install -r requirements.txt
```

## 事前準備・推奨環境

- [Copy HTML](https://chromewebstore.google.com/detail/copy-html/indfogjkdbmkihaohndcnkoaheopbhjf)（Chrome 拡張）をインストールしてください。

  - この拡張は、任意の HTML 要素をワンクリックでクリップボードにコピーするために使用します。
  - スクリプト内で「拡張ボタン」と呼んでいるのはこの Copy HTML Chrome 拡張のボタンです。

- スクリプト実行前に、**Twitter の検索画面**（ https://twitter.com/search ）を開いておいてください。
- キーワードや日付条件（since/until 句）はスクリプトが自動で入力します。
- スクリプトはこの検索画面上で自動的に検索クエリを入力し、「最新」タブを選択し、Copy HTML 拡張ボタンを押下して HTML を取得します。

## 使用方法

### 1. Twitter の HTML ファイルを自動で作成

```bash
python main.py html 250706
```

- 指定日付で Twitter 検索・最新タブ選択・拡張ボタン押下・HTML 保存まで自動化
- 初回実行時は「検索ボックス」「最新タブ」「拡張ボタン（Copy HTML Chrome 拡張）」の位置をマウスで指定
- `data/input/250706.html` が自動生成されます
- 既存ファイルがある場合は上書き確認を表示します

**注意:**

- Twitter の UI や Copy HTML 拡張の仕様が変わると動作しない場合があります
- 位置指定は毎回手動で行う必要があります（安全性・確実性のため）
- スクリプト実行前に必ず Twitter の検索画面 ( https://twitter.com/search ) を開いておいてください

### 2. HTML ファイルからツイートを抽出

```bash
python main.py extract 250706
```

- `data/input/250706.html` からツイートを抽出し、
  - `data/output/txt/250706.txt`（テキスト）
  - `data/output/json/250706.json`（JSON）
    に出力します
- **最後のツイート日時（until:...\_JST）がコンソールに表示され、同時にクリップボードにもコピーされます**
  - → 次回の検索条件としてすぐ貼り付け可能

### 3. 全ファイルをマージして CSV を作成

```bash
python main.py merge
```

- `data/output/csv/all_tweets.csv` に全ツイートを統合して出力します

## ファイル形式

### 入力ファイル

- HTML ファイル（クリップボードから自動生成）
- ファイル名形式：`YYMMDD.html`（例：`250706.html`）

### 出力ファイル

- テキストファイル（.txt）
- JSON ファイル（.json）
- CSV ファイル（.csv）

## 注意事項

- 入力 HTML ファイルはスクリプトで自動生成されます（手動配置不要）
- 出力ファイルは`data/output`フォルダに自動生成されます
- 日時は JST（日本標準時）で表示されます
- ツイートの重複は排除されません（元の HTML の構造に依存）
- **until 日付は自動的にクリップボードにコピーされます（次回検索条件用）**
- **HTML ファイル作成時は、クリップボードに HTML 要素がコピーされていることを確認してください**
- **自動化機能（html コマンド）は pyautogui を使用するため、ブラウザの位置設定が必要です**
- **自動化できる範囲：Twitter 検索、最新タブ選択、拡張ボタン押下、HTML 保存まで。Twitter の UI や拡張ボタン仕様変更には非対応。位置指定は毎回手動。**

## トラブルシューティング

### よくある問題

1. **ファイルが見つからないエラー**

   - `python main.py html <日付>` で HTML ファイルを作成したか確認
   - クリップボードに HTML 要素が正しくコピーされているか確認

2. **抽出件数が少ない**

   - HTML ファイルの構造を確認
   - セレクタが適切に動作しているか確認

3. **日時が正しく表示されない**
   - HTML ファイルの`datetime`属性を確認
   - タイムゾーン変換が正しく動作しているか確認

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

## 更新履歴

- v1.2.0: Twitter HTML 自動化機能のアップグレード

  - Twitter の HTML ファイル作成を自動化（html コマンドで一貫自動化）
  - pyautogui を使用したブラウザ操作の自動化
  - 位置指定・検索・最新タブ選択・拡張ボタン押下・HTML 保存まで自動化
  - main.py の html コマンドで日付指定 → 自動保存
  - クリップボード保存用スクリプトの役割を統合

- v1.1.0: クリップボード機能追加

  - until 日付のクリップボード自動コピー機能（次回検索条件用）
  - クリップボードから HTML ファイル作成機能
  - main.py に html コマンド追加
  - pyperclip 依存関係追加

- v1.0.0: 初期リリース
  - HTML ファイルからのツイート抽出機能
  - テキスト・JSON 出力機能
  - CSV 変換機能
  - マージ機能
