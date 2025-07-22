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

# 設定ファイルをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

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

def save_html_to_file(html_content, date_str, keyword_type='default'):
    # date_str: '2025-07-09' または '250709' など
    if '-' in date_str:  # YYYY-MM-DD形式
        # 2025-07-10 -> 250710
        parts = date_str.split('-')
        if len(parts) == 3:
            year = parts[0]
            month = parts[1]
            day = parts[2]
            yymmdd = f"{year[2:]}{month}{day}"  # 2025 -> 25, 07, 10 -> 250710
        else:
            print(f"エラー: 不正な日付形式です: {date_str}")
            return None
    elif len(date_str) == 6:  # YYMMDD形式
        yymmdd = date_str  # そのまま使用
    else:
        print(f"エラー: 不正な日付形式です: {date_str}")
        return None

    # prefixに基づいてフォルダを決定
    prefix = config.KEYWORD_PREFIX_MAPPING.get(keyword_type)
    folders = config.get_prefix_folders(prefix)
    output_dir = folders['input']

    # フォルダを作成
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{yymmdd}.html"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTMLファイルを保存しました: {filepath}")
    return filepath

def main(date_str=None, search_keyword=None, use_date=True, keyword_type='default'):
    if date_str is None:
        parser = argparse.ArgumentParser(description='TwitterのHTMLファイルを自動生成')
        parser.add_argument('date', help='検索対象の日付 (YYMMDD形式)')
        parser.add_argument('--search-keyword', default=None,
                           help='検索キーワード (デフォルト: 設定ファイルから取得)')
        parser.add_argument('--keyword-type', '-k', choices=['default', 'thai', 'en', 'chikirin', 'custom'],
                           default='default', help='検索キーワードの種類')
        parser.add_argument('--no-date', action='store_true',
                           help='日付指定なしで検索する')
        args = parser.parse_args()
        date_str = args.date
        search_keyword = args.search_keyword
        keyword_type = args.keyword_type
        use_date = not args.no_date

    # 検索キーワードの決定
    if search_keyword is None:
        if keyword_type == 'custom':
            search_keyword = input("検索キーワードを入力してください: ")
        else:
            search_keyword = config.SEARCH_KEYWORDS.get(keyword_type, config.DEFAULT_SEARCH_KEYWORD)

    # クリップボードからuntil日時を取得
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content.startswith('until:'):
            until_datetime = clipboard_content
            print(f"クリップボードからuntil日時を取得: {until_datetime}")

            # --no-dateの場合のみ、クリップボードの日時を使用
            if not use_date:
                # until:2025-05-08_16:54:40_JST から 250508 を生成
                try:
                    # until:2025-05-08_16:54:40_JST の形式をパース
                    import re
                    match = re.match(r'until:(\d{4})-(\d{2})-(\d{2})_\d{2}:\d{2}:\d{2}_JST', until_datetime)
                    if match:
                        year = match.group(1)
                        month = match.group(2)
                        day = match.group(3)
                        # YYMMDD形式に変換
                        date_str = f"{year[2:]}{month}{day}"  # 2025 -> 25, 05, 08 -> 250508
                        print(f"クリップボードの日時からファイル名用日付を生成: {date_str}")
                    else:
                        print(f"エラー: クリップボードのuntil日時の形式が正しくありません: {until_datetime}")
                        print("期待される形式: until:YYYY-MM-DD_HH:MM:SS_JST")
                        sys.exit(1)
                except Exception as e:
                    print(f"until日時のパースに失敗: {e}")
                    sys.exit(1)
            else:
                # 通常の場合は、指定された日付の23:59:59を使用（クリップボードは無視）
                until_datetime = f"until:{date_str}_23:59:59_JST"
                print(f"指定された日付のuntil日時を使用: {until_datetime}")
        else:
            # --no-dateの場合、クリップボードにuntil日時がない場合はエラー
            if not use_date:
                print("エラー: --no-dateオプション使用時は、クリップボードにuntil日時が必要です")
                print("期待される形式: until:YYYY-MM-DD_HH:MM:SS_JST")
                sys.exit(1)
            else:
                # 通常の場合は、指定された日付の23:59:59を使用
                until_datetime = f"until:{date_str}_23:59:59_JST"
                print(f"指定された日付のuntil日時を使用: {until_datetime}")
    except Exception as e:
        print(f"クリップボードの読み取りに失敗: {e}")
        if not use_date:
            print("エラー: --no-dateオプション使用時は、クリップボードにuntil日時が必要です")
            sys.exit(1)
        else:
            until_datetime = f"until:{date_str}_23:59:59_JST"
            print(f"指定された日付のuntil日時を使用: {until_datetime}")

    # 日付指定ありの場合のみ、日付の形式を確認
    if use_date:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_str = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print("エラー: 日付は YYYY-MM-DD 形式で入力してください")
            sys.exit(1)

    # 検索クエリを構築
    if use_date:
        search_query = f"since:{date_str}_00:00:00_JST {until_datetime} {search_keyword}"
    else:
        search_query = f"{until_datetime} {search_keyword}"
    print(f"検索クエリ: {search_query}")
    print("位置設定を開始します...")
    # 各位置を取得
    print("\n=== 位置設定 ===")
    search_box_pos = get_position("検索ボックスの位置(✗ボタンの位置)にマウスを移動してください")
    extension_button_pos = get_position("ブラウザ拡張ボタンの位置にマウスを移動してください")

    print("\n=== 自動化開始 ===")
    time.sleep(0.5)

    try:
        # Twitterの検索を実行
        print("Twitterの検索を実行中...")
        navigate_to_twitter_search(search_query, search_box_pos)

        # “最新”タブをクリック（除外済み）
        # print("“最新”タブをクリックします...")
        # pyautogui.click(latest_tab_pos)
        # time.sleep(1)  # タブ切り替えの待機

        # ページの読み込みを待機
        print("ページの読み込みを待機中...")
        time.sleep(2)

        # ブラウザ拡張ボタンでHTMLをコピー
        print("HTMLをコピー中...")
        html_content = copy_html_with_extension(extension_button_pos)

        if html_content:
            # HTMLファイルに保存
            filepath = save_html_to_file(html_content, date_str, keyword_type)
            print(f"処理が完了しました！ファイル: {filepath}")
            return filepath  # 成功時はファイルパスを返す
        else:
            print("エラー: HTMLの取得に失敗しました")
            return None  # 失敗時はNoneを返す

    except KeyboardInterrupt:
        print("\n処理が中断されました")
        return None
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None

if __name__ == "__main__":
    main()
