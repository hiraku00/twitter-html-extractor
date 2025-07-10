#!/usr/bin/env python3
"""
TwitterのHTMLファイル作成を自動化するスクリプト
日付を引数として受け取り、指定された日付でTwitter検索を実行し、
ブラウザ拡張ボタンでHTMLをコピーしてファイルに保存する
"""

import pyautogui
import time
import pyperclip
import sys
import os
from datetime import datetime
import argparse

def get_position(prompt):
    """指定された位置をユーザーにクリックさせて取得する"""
    print(prompt)
    input("準備ができたらEnterキーを押してください...")
    position = pyautogui.position()
    print(f"取得した座標: {position}")

    while True:
        confirmation = input("この座標でよろしいですか？ (yes/no): ").lower()
        if confirmation in ['yes', 'y']:
            return position
        elif confirmation in ['no', 'n']:
            print("再度クリックしてください。")
            input("準備ができたらEnterキーを押してください...")
            position = pyautogui.position()
            print(f"取得した座標: {position}")
        else:
            print("yes または no で答えてください。")

def navigate_to_twitter_search(search_query, search_box_pos):
    """Twitterの検索ボックスに検索クエリを入力する"""
    # 検索ボックスをクリック
    pyautogui.click(search_box_pos)
    time.sleep(1)

    # 既存の内容をクリア（Ctrl+A）
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.5)

    # 検索クエリを入力
    pyautogui.write(search_query, interval=0.01)
    time.sleep(0.5)

    # Enterキーを押して検索を実行
    pyautogui.press('enter')
    time.sleep(3)  # 検索結果の読み込みを待つ

def copy_html_with_extension(extension_button_pos):
    """ブラウザ拡張ボタンを押してHTMLをクリップボードにコピー"""
    # 拡張ボタンをクリック
    pyautogui.click(extension_button_pos)
    time.sleep(2)  # コピー処理の完了を待つ

    # クリップボードからHTMLを取得
    html_content = pyperclip.paste()
    return html_content

def save_html_to_file(html_content, date_str):
    """HTMLコンテンツをファイルに保存"""
    # 出力ディレクトリを作成
    output_dir = "data/input"
    os.makedirs(output_dir, exist_ok=True)

    # ファイル名を生成
    filename = f"twitter_{date_str}.html"
    filepath = os.path.join(output_dir, filename)

    # HTMLファイルに保存
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTMLファイルを保存しました: {filepath}")
    return filepath

def main():
    parser = argparse.ArgumentParser(description='TwitterのHTMLファイルを自動生成')
    parser.add_argument('date', help='検索対象の日付 (YYYY-MM-DD形式)')
    parser.add_argument('--search-keyword', default='dtv ビザ',
                       help='検索キーワード (デフォルト: dtv ビザ)')

    args = parser.parse_args()

    # 日付の形式を確認
    try:
        date_obj = datetime.strptime(args.date, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        print("エラー: 日付は YYYY-MM-DD 形式で入力してください")
        sys.exit(1)

    # 検索クエリを構築
    search_query = f'since:{date_str}_00:00:00_JST until:{date_str}_23:59:59_JST {args.search_keyword}'

    print(f"検索クエリ: {search_query}")
    print("位置設定を開始します...")

    # 各位置を取得
    print("\n=== 位置設定 ===")
    search_box_pos = get_position("Twitterの検索ボックスの位置にマウスを移動してください")
    extension_button_pos = get_position("ブラウザ拡張ボタンの位置にマウスを移動してください")

    print("\n=== 自動化開始 ===")
    print("5秒後に処理を開始します...")
    time.sleep(5)

    try:
        # Twitterの検索を実行
        print("Twitterの検索を実行中...")
        navigate_to_twitter_search(search_query, search_box_pos)

        # 少し待機してページの読み込みを待つ
        print("ページの読み込みを待機中...")
        time.sleep(5)

        # ブラウザ拡張ボタンでHTMLをコピー
        print("HTMLをコピー中...")
        html_content = copy_html_with_extension(extension_button_pos)

        if html_content:
            # HTMLファイルに保存
            filepath = save_html_to_file(html_content, date_str)
            print(f"処理が完了しました！ファイル: {filepath}")
        else:
            print("エラー: HTMLの取得に失敗しました")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
