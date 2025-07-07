#!/usr/bin/env python3
"""
Twitter HTML Extractor - Main Entry Point
"""

import sys
import os

# srcフォルダをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract_tweets_from_html import main as extract_main
from merge_all_txt_to_csv import merge_all_txt_to_csv

def main():
    """メインエントリーポイント"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  ツイート抽出: python main.py extract <日付>")
        print("  マージ実行:   python main.py merge")
        print("")
        print("例:")
        print("  python main.py extract 250706")
        print("  python main.py merge")
        sys.exit(1)

    command = sys.argv[1]

    if command == "extract":
        if len(sys.argv) < 3:
            print("エラー: 日付を指定してください")
            print("例: python main.py extract 250706")
            sys.exit(1)

        # extract_tweets_from_html.pyのmain関数を呼び出し
        # 引数を調整して渡す
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        extract_main()

    elif command == "merge":
        merge_all_txt_to_csv()

    else:
        print(f"エラー: 不明なコマンド '{command}'")
        print("使用可能なコマンド: extract, merge")
        sys.exit(1)

if __name__ == "__main__":
    main()
