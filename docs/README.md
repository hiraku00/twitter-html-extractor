# Twitter HTML Extractor

## 概要

Twitter/X の検索結果 HTML からツイート情報を自動抽出・整理・保存するツールです。検索条件の自動入力・HTML 保存・抽出・整形・CSV 化まで一気通貫で自動化できます。

## 主な特徴

- 検索条件や保存先、キーワードは設定ファイルで柔軟に管理可能
- 「次回検索用 until 日時」を自動でクリップボードにコピー
- 検索条件の違いをコマンドオプションで柔軟に指定可能
- テストも充実、安心してカスタマイズ可能
- シンプルなコマンドラインインターフェース
- 連続実行モードでマウスポジションを保存・再利用可能
- 詳細なログ出力でデバッグをサポート

補足: マウスポジションは `data/config/positions.json` に保存されます。TTY環境では実行時に「保存された位置を使用しますか？［y/N］」が表示されます。yで保存位置を使用、nで再取得します（非TTYでは自動で保存位置を使用）。

## インストール

```bash
git clone <repository-url>
cd twitter-html-extractor
pip install -r requirements.txt
```

## テストの実行

```bash
# すべてのテストを実行
python -m pytest tests/

# 詳細な出力付きでテストを実行
python -m pytest -v tests/

# 特定のテストファイルを実行
python -m pytest tests/test_args.py

# 特定のテスト関数を実行
python -m pytest tests/test_args.py::TestArgumentParser::test_all_with_no_date

# カバレッジレポートを生成
pytest --cov=src tests/
```

## セットアップ・事前準備

- Python 3.7 以上
- [Copy HTML](https://chromewebstore.google.com/detail/copy-html/indfogjkdbmkihaohndcnkoaheopbhjf)（Chrome 拡張）をインストール
- スクリプト実行前に **Twitter の検索画面**（ https://twitter.com/search ）を開いておく
- キーワードや日付条件（since/until 句）はスクリプトが自動で入力
- スクリプトはこの検索画面上で自動的に検索クエリを入力し、Copy HTML 拡張ボタンを押下して HTML を取得
 - マウスポジションはリポジトリ内 `data/config/positions.json` に保存・再利用されます（TTYでは実行時に使用可否を確認）

## 基本的な使い方

### 一括実行（推奨）

```bash
# 最新のツイートを取得（現在日時を使用）
python main.py all --no-date -k manekineko

# 特定の日付のツイートを取得（YYMMDD形式）
python main.py all 250831 -k chikirin

# 詳細表示モードで実行
python main.py all 250831 -k manekineko --verbose

# 連続実行モードで実行（-c は --continuous の短縮形）
python main.py all 250831 -k manekineko -c 10
```

### HTMLファイルの作成

```bash
# 基本形（日付指定）
python main.py html 250706

# 日付指定なし（現在日時を使用）
python main.py html --no-date

# キーワードタイプを指定
python main.py html 250706 -k chikirin
```

- 指定日（例: 2025/07/06）の 0:00:00〜23:59:59 で検索
- `--no-date` を指定すると、クリップボードから `until:YYYY-MM-DD_HH:MM:SS_JST` 形式の日時を取得
- `--search-keyword` でカスタム検索キーワードを指定可能
- `-k, --keyword-type` で事前に設定したキーワードタイプを指定可能
- 結果は `data/input/250706.html` に保存され、自動的に抽出処理も実行

### ツイートの抽出（既存HTMLから）

```bash
# 基本形（最新のHTMLファイルから抽出）
python main.py extract -k manekineko

# 特定の日付のHTMLから抽出
python main.py extract 250706 -k chikirin

# 詳細表示モードで実行
python main.py extract 250706 -k manekineko --verbose
```

- 既存のHTMLファイルからツイートを抽出
- 日付形式は `YYMMDD`
- 結果は `data/output/` に保存

```bash
# 基本形
python main.py extract 250706

# キーワードタイプを指定
python main.py extract 250706 --keyword-type en

# 詳細表示モード
python main.py extract 250706 -v
```

- 指定した日付のHTMLファイルからツイートを抽出
- 抽出結果は `data/output/txt/` と `data/output/json/` に保存

### テキストファイルのマージ

```bash
# 基本形
python main.py merge

# 特定のキーワードタイプのみマージ
python main.py merge --keyword-type chikirin

# 詳細表示モード
python main.py merge -v
```

- 抽出済みのテキストファイルを1つのCSVに結合
- デフォルトでは `data/output/csv/all_tweets.csv` に出力
- キーワードタイプを指定すると、該当するフォルダ内のファイルのみを処理

### キーワードタイプを指定する方法

キーワードタイプは以下のいずれかの形式で指定できます：
- `--keyword-type`（完全形）
- `--k`（短縮形）
- `-k`（短縮形）

例：
```bash
# 以下の3つはすべて同じ意味
python main.py html 250803 --keyword-type chikirin
python main.py html 250803 --k chikirin
python main.py html 250803 -k chikirin
```

### 一括実行（HTML作成 + 抽出）

```bash
# 基本形
python main.py all 250706

# 日付指定なし（クリップボードから日時を取得）
python main.py all --no-date

# カスタム検索キーワードを指定
python main.py all 250706 --search-keyword "from:example"

# キーワードタイプを指定
python main.py all 250706 -k chikirin
```

- `all` サブコマンドはHTML作成と抽出を一括で実行
- `--no-date` と併用すると、クリップボードから `until:YYYY-MM-DD_HH:MM:SS_JST` 形式の日時を取得
- HTMLの作成とツイート抽出を一括で実行
- 個別に `html` と `extract` を実行するのと同じ

### 連続実行モード

連続実行モードを使用すると、初回実行時に指定したマウスポジションを保存し、次回以降は自動的に使用できます。

```bash
# 初回実行（マウスポジションを指定）
python main.py all 250831 -k chikirin --continuous 10
# または短縮形 -c を使用
python main.py all 250831 -k chikirin -c 10

# 2回目以降（保存されたマウスポジションを使用）
python main.py all 250901 -k chikirin -c 10
```

**パラメーター**:
- `--continuous` または `-c`: 連続実行モードを有効にします
- `回数`（必須）: 取得するツイートの回数を指定します

**注意**: 
- ブラウザのレイアウトや解像度を変更した場合は、再度 `--continuous` フラグを指定してマウスポジションを再設定してください。
- `回数` パラメーターは必ず指定してください。
 - マウスポジションは `data/config/positions.json` に保存されます。TTYでは都度「保存された位置を使用しますか？［y/N］」の確認があります。yで保存位置を使用します。

### キーワード指定オプション

```bash
# キーワードタイプを指定（--keyword-type または短縮形 -k）
python main.py --html 250706 --keyword-type en  # 完全形
python main.py --html 250706 -k en             # 短縮形

# カスタムキーワードで検索
python main.py --html 250706 --search-keyword "ニュース ビザ"

# キーワードタイプに chikirin を指定
python main.py --html 250706 -k chikirin
```

- `--keyword-type` の代わりに短縮形の `-k` が使用可能
- 設定ファイルで定義されたキーワードタイプか、`--search-keyword` で直接キーワードを指定
- `chikirin` などのキーワードタイプを指定すると、専用フォルダにファイルが保存され、データが整理されます

### キーワードタイプ別フォルダ機能

キーワードタイプを指定すると、自動的に専用フォルダが作成され、データが分離管理されます：

- **デフォルトキーワード**: `data/input/`, `data/output/txt/`, `data/output/json/`, `data/output/csv/`
- **chikirin キーワード**: `data/input/chikirin/`, `data/output/chikirin/txt/`, `data/output/chikirin/json/`, `data/output/chikirin/csv/`
- **その他のキーワード**: `data/input/{prefix}/`, `data/output/{prefix}/txt/`, `data/output/{prefix}/json/`, `data/output/{prefix}/csv/`

この機能により、異なる検索条件のデータを混在させることなく、整理して管理できます。

### キーワードタイプ別のデータ管理

キーワードタイプを指定すると、自動的に専用フォルダが作成され、データが分離管理されます：

- **デフォルトキーワード**: 
  - `data/input/`
  - `data/output/txt/`
  - `data/output/json/`
  - `data/output/csv/all_tweets.csv`

- **chikirin キーワード**: 
  - `data/input/chikirin/`
  - `data/output/chikirin/txt/`
  - `data/output/chikirin/json/`
  - `data/output/chikirin/csv/chikirin_tweets.csv`

- **その他のキーワード**: 
  - `data/input/{prefix}/`
  - `data/output/{prefix}/txt/`
  - `data/output/{prefix}/json/`
  - `data/output/{prefix}/csv/{keyword_type}_tweets.csv`

これにより、異なる検索条件のデータを混在させることなく、整理して管理できます。

---

## コマンド例・検索クエリ・前提条件

| コマンド例                                           | 検索クエリの例                                                                   | 注意点                                                           |
| ---------------------------------------------------- | -------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `python main.py --html 250706`                       | `since:2025-07-06_00:00:00_JST until:2025-07-06_23:59:59_JST dtv ビザ`            | なし（コマンド引数のみで OK）                                     |
| `python main.py --html --no-date`                    | `until:2025-07-06_12:34:56_JST dtv ビザ`                                          | クリップボードに`until:YYYY-MM-DD_HH:MM:SS_JST`形式の文字列が必要 |
| `python main.py --html 250803 --keyword-type chikirin` | `since:2025-08-03_00:00:00_JST until:2025-08-03_23:59:59_JST ちきりん ビザ`      | `--keyword-type` は `--k` または `-k` でも可 |
| `python main.py --html 250706 -k chikirin`           | `since:2025-07-06_00:00:00_JST until:2025-07-06_23:59:59_JST #ちきりんセレクトTV` | なし（コマンド引数のみで OK）<br>`-k` は `--keyword-type` の短縮形 |
| `python main.py --extract 250706`                    | -                                                                                | 指定した日付のHTMLからツイートを抽出                              |
| `python main.py --merge`                             | -                                                                                | 抽出済みのテキストファイルをCSVに結合                             |
| `python main.py --auto 250706`                       | `since:2025-07-06_00:00:00_JST until:2025-07-06_23:59:59_JST`（自動設定）         | HTML作成とツイート抽出を一括実行                                  |

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
  - `python main.py merge`: デフォルトキーワードタイプのファイルをマージして CSV 作成
  - `python main.py merge --keyword-type <type>` または `-k <type>`: 特定キーワードタイプのみマージ
  - 使用可能なキーワードタイプ: `default`, `thai`, `en`, `chikirin`, `custom`

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
│   └── create_twitter_html_all.py
├── data/                         # データフォルダ
│   ├── input/                    # 入力ファイル（スクリプトで自動生成）
│   │   └── chikirin/            # chikirinキーワード用専用フォルダ
│   ├── output/                   # 出力ファイル
│       ├── txt/                  # テキストファイル
│       ├── json/                 # JSONファイル
│       ├── csv/                  # CSVファイル
│       └── chikirin/            # chikirinキーワード用専用フォルダ
│           ├── txt/              # テキストファイル
│           ├── json/             # JSONファイル
│           └── csv/              # CSVファイル
│   └── config/                   # 設定（マウスポジションなど）
│       └── positions.json        # 保存されたマウスポジション
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

### [Unreleased]
- 連続実行モード（`--continuous` フラグ）を追加
- 引数処理のスコープ問題を修正
- エラーハンドリングを強化
- 位置情報の保存/読み込み機能を追加
- ログ出力を体系化し、デバッグを容易に

### [1.0.0] - 2025-XX-XX

- v1.6.0: キーワードタイプ別フォルダ機能と分離マージ機能の実装
  - キーワードタイプ指定時に prefix 別フォルダが自動作成される機能を実装
  - HTML ファイルの自動検出機能（prefix 別フォルダ優先）を実装
  - マージ機能に--keyword-type オプションを追加（特定キーワードタイプのみマージ）
  - 分離 CSV ファイル作成機能を実装（all_tweets.csv, chikirin_tweets.csv 等）
  - prefix 別データフォルダ用の gitignore パターンを追加
- v1.5.0: chikirin キーワードタイプの追加と prefix 別フォルダ機能
  - "#ちきりんセレクト TV"キーワードと"chikirin"prefix を追加
  - prefix 別の専用フォルダ作成機能（`data/input/chikirin/`、`data/output/chikirin/`）
  - HTML 作成、抽出、マージ処理で prefix 別フォルダを自動検出・使用
  - 設定ファイルにキーワードタイプと prefix のマッピング機能を追加
  - テストケースの追加と更新
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
