#!/usr/bin/env python3
"""
クリップボードの内容からHTMLファイルを作成するスクリプト
"""

import pyperclip
import argparse
import os
import sys
from datetime import datetime

def create_html_from_clipboard(filename):
    """クリップボードの内容からHTMLファイルを作成"""

    try:
        # クリップボードから内容を取得
        clipboard_content = pyperclip.paste()

        if not clipboard_content.strip():
            print("エラー: クリップボードに内容がありません。")
            print("開発者コンソールでHTML要素をコピーしてから実行してください。")
            return False

        # 入力フォルダの確認・作成
        input_folder = "data/input"
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
            print(f"入力フォルダ '{input_folder}' を作成しました。")

        # HTMLファイルパス
        html_file_path = os.path.join(input_folder, f"{filename}.html")

        # 既存ファイルの確認
        if os.path.exists(html_file_path):
            print(f"警告: ファイル '{html_file_path}' は既に存在します。")
            response = input("上書きしますか？ (y/N): ")
            if response.lower() != 'y':
                print("処理を中止しました。")
                return False

        # HTMLファイルを作成
        with open(html_file_path, 'w', encoding='utf-8') as f:
            f.write(clipboard_content)

        print(f"HTMLファイルを作成しました: {html_file_path}")
        print(f"ファイルサイズ: {len(clipboard_content)} 文字")

        # 作成日時を記録
        creation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"作成日時: {creation_time}")

        return True

    except Exception as e:
        print(f"エラー: HTMLファイルの作成に失敗しました: {e}")
        return False

def main():
    """メイン処理"""
    parser = argparse.ArgumentParser(description='クリップボードの内容からHTMLファイルを作成します')
    parser.add_argument('filename', help='ファイル名（例: 250701, 250624）')

    args = parser.parse_args()

    print(f"クリップボードの内容からHTMLファイル '{args.filename}.html' を作成します...")

    success = create_html_from_clipboard(args.filename)

    if success:
        print("\n次のコマンドでツイートを抽出できます:")
        print(f"python src/extract_tweets_from_html.py {args.filename}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
