# Twitter HTML Extractor

## 概要

Twitter/X の検索結果 HTML からツイート情報を自動抽出・整理・保存するツールです。検索条件の自動入力・HTML 保存・抽出・整形・CSV 化まで一気通貫で自動化できます。

## 主な特徴

- 検索条件や保存先、キーワードは設定ファイルで柔軟に管理可能
- 「次回検索用 until 日時」を自動でクリップボードにコピー
- 検索条件の違いをコマンドオプションで柔軟に指定可能
- テストも充実、安心してカスタマイズ可能

## インストール

```bash
git clone <repository-url>
cd twitter-html-extractor
pip install -r requirements.txt
```

## セットアップ・事前準備

- Python 3.7 以上
- [Copy HTML](https://chromewebstore.google.com/detail/copy-html/indfogjkdbmkihaohndcnkoaheopbhjf)（Chrome 拡張）をインストール
- スクリプト実行前に **Twitter の検索画面**（ https://twitter.com/search ）を開いておく
- キーワードや日付条件（since/until 句）はスクリプトが自動で入力
- スクリプトはこの検索画面上で自動的に検索クエリを入力し、Copy HTML 拡張ボタンを押下して HTML を取得

## 基本的な使い方

### 日付指定（推奨・基本）

```bash
python main.py html 250706
```

- 指定日（例: 2025/07/06）の 0:00:00〜23:59:59 で検索
- 設定ファイルのキーワードで検索（`--keyword-type`や`--search-keyword`で変更可）
- `data/input/250706.html`が自動生成され、同時に抽出・保存も完了

### 日付指定なし（--no-date）

```bash
python main.py html --no-date
```

- クリップボードに`until:YYYY-MM-DD_HH:MM:SS_JST`形式の until 日時が必要
- since 指定なし、until はクリップボードから取得
- `data/input/YYMMDD.html`（until 日時から日付自動生成）が作成され、同時に抽出・保存も完了

### キーワード指定

```bash
python main.py html 250706 --keyword-type en
python main.py html 250706 --search-keyword "ニュース ビザ"
```

- 設定ファイルのキーワード種類やカスタムキーワードで検索可能

---

## コマンド例・検索クエリ・前提条件

| コマンド例                      | 変換される検索クエリ                                                   | 前提条件（クリップボード等）                                      |
| ------------------------------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `python main.py html 250706`    | `since:2025-07-06_00:00:00_JST until:2025-07-06_23:59:59_JST dtv ビザ` | なし（コマンド引数のみで OK）                                     |
| `python main.py html --no-date` | `until:2025-07-06_12:34:56_JST dtv ビザ`                               | クリップボードに`until:YYYY-MM-DD_HH:MM:SS_JST`形式の文字列が必要 |

---

## クリップボード until の使い方・具体的なユースケース

### 1. 初回（例：2025 年 7 月 6 日分）を取得

```bash
python main.py html 250706
```

- 検索クエリ：
  `since:2025-07-06_00:00:00_JST until:2025-07-06_23:59:59_JST dtv ビザ`
- 取得したツイートのうち、最も古いツイートの日時（例：`2025-07-06 12:34:56`）が
  `until:2025-07-06_12:34:56_JST` という形式でクリップボードに自動コピーされる

### 2. さらに前日以前のツイートを取得したい場合（繰り返し取得）

```bash
python main.py html --no-date
```

- クリップボードの内容（例：`until:2025-07-06_12:34:56_JST`）が検索クエリの until に使われる
- 検索クエリ：
  `until:2025-07-06_12:34:56_JST dtv ビザ`
- これにより「前回取得した最古ツイートよりさらに前のツイート」を取得できる

### 3. 以降、繰り返し

- 2 回目の取得でもっと古いツイートが見つかれば、その最古ツイートの日時がまたクリップボードにコピーされる
- そのまま `python main.py html --no-date` を繰り返すことで、どんどん過去に遡ってツイートを取得できる

**ポイント**

- 初回は日付指定で「その日全体」を取得
- 2 回目以降は「前回の最古ツイートより前（until）」で繰り返し取得
- クリップボードの内容はツールが自動で更新するので、ユーザーはコマンドを繰り返すだけで OK

---

## 詳細な仕様・オプション説明

- **html コマンド**
  - `python main.py html <YYMMDD>`: 指定日付で検索・保存・抽出
  - `python main.py html --no-date`: クリップボードの until 日時で検索・保存・抽出
  - `--keyword-type`, `--search-keyword` でキーワード指定可
- **extract コマンド**
  - `python main.py extract <YYMMDD>`: 既存 HTML から抽出のみ
- **merge コマンド**
  - `python main.py merge`: 全ファイルをマージして CSV 作成

---

## テスト

- テストは`tests/`配下に充実
- 実行方法:
  ```bash
  python -m unittest discover tests
  ```
- pyautogui や get_position 等のマウス操作・ユーザー入力はテスト時に自動でモックされ、実際の操作は発生しません

---

## FAQ・トラブルシューティング

1. **ファイルが見つからないエラー**
   - `python main.py html <日付>` で HTML ファイルを作成したか確認
   - クリップボードに HTML 要素が正しくコピーされているか確認
2. **抽出件数が少ない**
   - HTML ファイルの構造を確認
   - セレクタが適切に動作しているか確認
3. **日時が正しく表示されない**
   - HTML ファイルの`datetime`属性を確認
   - タイムゾーン変換が正しく動作しているか確認
4. **日付引数エラー**
   - 日付は YYMMDD 形式（例：250706）で指定してください
   - 通常の html コマンドでは日付引数が必須です
5. **--no-date オプションでエラー**
   - クリップボードに until 日時（until:YYYY-MM-DD_HH:MM:SS_JST 形式）が必要です

---

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
├── config.py                     # 設定ファイル
├── requirements.txt
└── .gitignore
```

---

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。

---

## 更新履歴

- v1.4.0: html コマンドの動作改善と--no-date オプションの追加
  - 通常の html コマンドで日付引数が必須に変更（YYMMDD 形式のみ）
  - `--no-since`を`--no-date`にリネーム（より分かりやすく）
  - 通常の html コマンドではクリップボードを使用せず、指定された日付の 23:59:59 を使用
  - --no-date オプションではクリップボードの until 日時が必須
  - 自動 extract 機能の追加（html コマンド実行時に自動的に extract 処理も実行）
  - エラーメッセージの改善（日付未指定・不正形式時）
  - テストの改善（pyautogui をモックしてテスト時の副作用を防止）
- v1.3.0: 設定ファイル化と since 指定オプション追加
  - 設定ファイル（config.py）の導入
  - 検索キーワードの外部化と種類別管理
  - since 指定なしでの検索オプション（--no-since）
  - カスタム検索キーワード指定オプション（--search-keyword）
  - 検索キーワード種類指定オプション（--keyword-type）
  - ファイルパス設定の統一化
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
