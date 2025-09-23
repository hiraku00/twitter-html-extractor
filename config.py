#!/usr/bin/env python3
"""
設定ファイル
検索キーワードやその他の設定を管理
"""

# デフォルトの検索キーワード
DEFAULT_SEARCH_KEYWORD = 'dtv ビザ'

# 検索キーワードの定義
SEARCH_KEYWORDS = {
    'default': 'dtv ビザ',
    'thai': 'dtv タイ',
    'en': 'dtv visa',
    'chikirin': '#ちきりんセレクトTV',
    'manekineko': 'from:thailandelitevi',
    'intmax': 'lang:ja "intmax" マイニング or mining',
    'custom': None  # カスタムキーワード用
}

# キーワードタイプとprefixのマッピング
KEYWORD_PREFIX_MAPPING = {
    'default': None,            # data/input/ 直下に保存
    'thai': 'thai',             # data/input/thai/ に保存
    'en': 'en',                 # data/input/en/ に保存
    'chikirin': 'chikirin',     # data/input/chikirin/ に保存
    'manekineko': 'manekineko', # data/input/manekineko/ に保存
    'intmax': 'intmax',         # data/input/intmax/ に保存
    'custom': 'custom'          # data/input/custom/ に保存
}

# ファイルパス設定
INPUT_FOLDER = "data/input"
OUTPUT_FOLDER = "data/output"
TXT_OUTPUT_FOLDER = "data/output/txt"
JSON_OUTPUT_FOLDER = "data/output/json"
CSV_OUTPUT_FOLDER = "data/output/csv"

# prefix別のフォルダ設定
def get_prefix_folders(prefix):
    """prefixに基づいてフォルダパスを取得"""
    if prefix is None:
        return {
            'input': INPUT_FOLDER,
            'output': OUTPUT_FOLDER,
            'txt': TXT_OUTPUT_FOLDER,
            'json': JSON_OUTPUT_FOLDER,
            'csv': CSV_OUTPUT_FOLDER
        }
    else:
        return {
            'input': f"data/input/{prefix}",
            'output': f"data/output/{prefix}",
            'txt': f"data/output/{prefix}/txt",
            'json': f"data/output/{prefix}/json",
            'csv': f"data/output/{prefix}/csv"
        }

# 日付形式設定
DATE_FORMAT = '%Y-%m-%d'
TIME_FORMAT = '%H:%M:%S'

# 検索クエリのテンプレート（クリップボードのuntil日時を使用）
SEARCH_QUERY_TEMPLATE_WITH_SINCE = 'since:{date}_00:00:00_JST {until_datetime} {keyword}'
SEARCH_QUERY_TEMPLATE_WITHOUT_SINCE = '{until_datetime} {keyword}'

# マウスポジション設定ファイルのパス
import os
CONFIG_DIR = os.path.expanduser("~/.config/twitter-html-extractor")
POSITION_CONFIG_PATH = os.path.join(CONFIG_DIR, "positions.json")

# デフォルトのマウスポジション設定
DEFAULT_POSITIONS = {
    'search_box': {'x': 0, 'y': 0},  # 検索ボックスの位置
    'extension_button': {'x': 0, 'y': 0}  # 拡張ボタンの位置
}

# デバッグ設定
DEBUG = False
