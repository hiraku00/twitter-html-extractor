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
    return position

def navigate_to_twitter_search(search_query, search_box_pos):
    """Twitterの検索ボックスに検索クエリを入力する"""
    # 検索ボックスをクリック
    pyautogui.click(search_box_pos)
    pyautogui.click(search_box_pos)
    time.sleep(0.5)

    # # 既存の内容をクリア（command + a）
    # pyautogui.hotkey('command', 'a')
    # time.sleep(0.5)
    # pyautogui.press('delete')
    # time.sleep(1)

    # 検索クエリをクリップボードにコピーして貼り付け
    import pyperclip
    pyautogui.click(search_box_pos)
    pyperclip.copy(search_query)
    print(f'search_query : {search_query}')
    pyautogui.hotkey('command', 'v')
    # time.sleep(0.5)

    # Enterキーを押して検索を実行
    pyautogui.press('enter')
    time.sleep(3)  # 検索結果の読み込みを待つ

def copy_html_with_extension(extension_button_pos):
    """ブラウザ拡張ボタンを押してHTMLをクリップボードにコピー"""
    # 拡張ボタンをクリック
    pyautogui.click(extension_button_pos)
    time.sleep(1)  # コピー処理の完了を待つ

    # クリップボードからHTMLを取得
    html_content = pyperclip.paste()
    return html_content

def save_html_to_file(html_content, date_str):
    # date_str: '2025-07-09' など
    yymmdd = date_str[2:4] + date_str[5:7] + date_str[8:10]  # '250709'
    output_dir = "data/input"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{yymmdd}.html"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTMLファイルを保存しました: {filepath}")
    return filepath

def main(date_str=None, search_keyword='ビザ dtv'):
    if date_str is None:
        parser = argparse.ArgumentParser(description='TwitterのHTMLファイルを自動生成')
        parser.add_argument('date', help='検索対象の日付 (YYYY-MM-DD形式)')
        parser.add_argument('--search-keyword', default='dtv ビザ',
                           help='検索キーワード (デフォルト: dtv ビザ)')
        args = parser.parse_args()
        date_str = args.date
        search_keyword = args.search_keyword
    # 日付の形式を確認
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        date_str = date_obj.strftime('%Y-%m-%d')
    except ValueError:
        print("エラー: 日付は YYYY-MM-DD 形式で入力してください")
        sys.exit(1)
    # 検索クエリを構築
    search_query = f'since:{date_str}_00:00:00_JST until:{date_str}_23:59:59_JST {search_keyword}'
    print(f"検索クエリ: {search_query}")
    print("位置設定を開始します...")
    # 各位置を取得
    print("\n=== 位置設定 ===")
    search_box_pos = get_position("検索ボックスの位置(✗ボタンの位置)にマウスを移動してください")
    latest_tab_pos = get_position("“最新”タブの位置にマウスを移動してください")
    extension_button_pos = get_position("ブラウザ拡張ボタンの位置にマウスを移動してください")

    print("\n=== 自動化開始 ===")
    time.sleep(0.5)

    try:
        # Twitterの検索を実行
        print("Twitterの検索を実行中...")
        navigate_to_twitter_search(search_query, search_box_pos)

        # “最新”タブをクリック
        print("“最新”タブをクリックします...")
        pyautogui.click(latest_tab_pos)
        time.sleep(1)  # タブ切り替えの待機

        # ページの読み込みを待機
        print("ページの読み込みを待機中...")
        time.sleep(2)

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
