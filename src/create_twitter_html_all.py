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

def get_position(prompt, test_mode=False):
    """指定された位置をユーザーにクリックさせて取得する"""
    if test_mode:
        from types import SimpleNamespace
        return SimpleNamespace(x=100, y=200)  # テスト用の固定座標
    print(prompt)
    input("準備ができたらEnterキーを押してください...")
    position = pyautogui.position()
    print(f"取得した座標: {position}")
    return position

def navigate_to_twitter_search(search_query, search_box_pos):
    """Twitterの検索ボックスに検索クエリを入力する"""
    # 検索ボックスをクリック & xボタンをクリック
    pyautogui.click(search_box_pos)
    pyautogui.click(search_box_pos)
    time.sleep(0.5)

    # 検索クエリをクリップボードにコピーして貼り付け
    import pyperclip
    pyautogui.click(search_box_pos)
    pyperclip.copy(search_query)
    print(f'search_query : {search_query}')
    pyautogui.hotkey('command', 'v')

    # Enterキーを押して検索を実行
    pyautogui.press('enter')
    time.sleep(1)  # 検索結果の読み込みを待つ

def copy_html_with_extension(extension_button_pos):
    """ブラウザ拡張ボタンを押してHTMLをクリップボードにコピー"""
    # 拡張ボタンをクリック
    pyautogui.click(extension_button_pos)
    time.sleep(0.5)  # コピー処理の完了を待つ

    # クリップボードからHTMLを取得
    html_content = pyperclip.paste()
    return html_content

def save_html_to_file(html_content, date_str, keyword_type='default', search_keyword=None):
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

    # 出力先ディレクトリを決定
    # コマンドライン引数で明示的に search_keyword が指定された場合のみ searchkeyword フォルダを使用
    if search_keyword is not None and any(arg.startswith('--search-keyword') for arg in sys.argv[1:] if arg != '--search-keyword'):
        # 明示的に検索キーワードが指定された場合はsearchkeywordフォルダに保存
        output_dir = os.path.join(config.INPUT_FOLDER, 'searchkeyword')
    else:
        # キーワードタイプに基づいてフォルダを決定
        prefix = config.KEYWORD_PREFIX_MAPPING.get(keyword_type, '')
        if prefix and keyword_type != 'default':
            output_dir = os.path.join(config.INPUT_FOLDER, prefix)
        else:
            output_dir = config.INPUT_FOLDER  # デフォルトはinput直下
    
    # フォルダを作成
    os.makedirs(output_dir, exist_ok=True)

    filename = f"{yymmdd}.html"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filepath

def main(test_mode=False, date_str=None, search_keyword=None, use_date=True, keyword_type='default', verbose=False, date_override=None):
    # コマンドライン引数として実行された場合の処理
    import sys
    
    # 直接パラメータで呼び出された場合の処理
    if date_override is not None:
        # date_overrideが指定されている場合はそれを使用
        date_str = date_override
    
    if date_str is not None or search_keyword is not None or not use_date or keyword_type != 'default' or verbose:
        # 直接パラメータで呼び出された場合、そのまま処理を続行
        pass
    # コマンドライン引数で呼び出された場合の処理
    elif len(sys.argv) > 1 and not any(arg.startswith('--search-keyword') or 
                                     arg.startswith('--keyword-type') or 
                                     arg.startswith('--no-date') or 
                                     arg.startswith('-k') for arg in sys.argv[1:]):
        # 引数として日付が指定されている場合
        parser = argparse.ArgumentParser(description='TwitterのHTMLファイルを自動生成')
        parser.add_argument('date', nargs='?', default=None, help='検索対象の日付 (YYMMDD形式)')
        parser.add_argument('--search-keyword', default=None,
                          help='検索キーワード (デフォルト: 設定ファイルから取得)')
        parser.add_argument('--keyword-type', '-k', default='default', 
                          help='検索キーワードの種類 (デフォルト: default)')
        parser.add_argument('--no-date', action='store_true',
                          help='日付指定なしで検索する')
        args = parser.parse_args()
        
        # 引数から値を設定
        date_str = args.date
        search_keyword = args.search_keyword or search_keyword
        keyword_type = args.keyword_type
        use_date = not args.no_date
        
        # date_overrideが指定されている場合は日付を上書き
        if date_override is not None:
            date_str = date_override
    
    # モジュールとして呼び出された場合の処理
    if date_str is None:
        parser = argparse.ArgumentParser(description='TwitterのHTMLファイルを自動生成')
        if use_date:
            parser.add_argument('date', nargs='?', default=None, help='検索対象の日付 (YYMMDD形式)')
        else:
            parser.add_argument('date', nargs='?', default=None, help='検索対象の日付 (YYMMDD形式、--no-dateの場合は無視されます)')
        parser.add_argument('--search-keyword', default=search_keyword,
                          help='検索キーワード (デフォルト: 設定ファイルから取得)')
        parser.add_argument('--keyword-type', '-k', default=keyword_type, 
                          help='検索キーワードの種類 (デフォルト: {})'.format(keyword_type))
        parser.add_argument('--no-date', action='store_true',
                          help='日付指定なしで検索する')
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='詳細な出力を有効化')
        args = parser.parse_args()
        
        # 引数から値を設定
        date_str = args.date
        search_keyword = args.search_keyword
        keyword_type = args.keyword_type
        use_date = not args.no_date
        verbose = args.verbose or verbose
        
        # date_overrideが指定されている場合は日付を上書き
        if date_override is not None:
            date_str = date_override
            use_date = True
    
    # 検索キーワードの決定
    if search_keyword is None:
        if keyword_type == 'custom':
            search_keyword = input("検索キーワードを入力してください: ")
        else:
            search_keyword = config.SEARCH_KEYWORDS.get(keyword_type, config.DEFAULT_SEARCH_KEYWORD)
    
    # 日付が指定されておらず、かつ日付を使用する場合はエラー
    if date_str is None and use_date and not test_mode:
        print("エラー: 日付が指定されていません。--no-date オプションを使用するか、日付を指定してください。")
        sys.exit(1)

    # until_datetime を初期化
    until_datetime = ""
    
    try:
        # 日付指定がある場合
        if use_date and date_str:
            # 日付形式をYYYY-MM-DDに変換（6桁形式の場合）
            if len(date_str) == 6 and date_str.isdigit():
                year = 2000 + int(date_str[:2])
                month = date_str[2:4]
                day = date_str[4:6]
                date_ymd = f"{year}-{month}-{day}"
            else:
                # 既にYYYY-MM-DD形式の場合はそのまま使用
                date_ymd = date_str
            
            # until日付を設定
            until_datetime = f"until:{date_ymd}_23:59:59_JST"
            print(f"指定された日付のuntil日時を使用: {until_datetime}")
            # 後続の処理で使用するためにdate_strを更新
            date_str = date_ymd
        elif not use_date:
            # クリップボードからuntil日時を取得
            import pyperclip
            clipboard_content = pyperclip.paste().strip()
            if clipboard_content.startswith('until:') and '_JST' in clipboard_content:
                until_datetime = clipboard_content
                print(f"クリップボードからuntil日時を取得: {until_datetime}")
                # 日付部分を抽出（例: until:2025-08-26_15:45:13_JST から 2025-08-26 を抽出）
                date_part = until_datetime.split('_')[0].replace('until:', '')
                date_ymd = date_part.split(' ')[0]  # 日付部分のみを取得
                date_str = date_ymd
                print(f"クリップボードの日時からファイル名用日付を生成: {date_str.replace('-', '')}")
            else:
                # 現在時刻を使用
                now = datetime.now()
                until_datetime = now.strftime("until:%Y-%m-%d_%H:%M:%S_JST")
                date_str = now.strftime("%Y-%m-%d")
                print(f"現在時刻のuntil日時を使用: {until_datetime}")
        else:
            # --no-date の場合はクリップボードを確認
            clipboard_content = pyperclip.paste()
            if clipboard_content and isinstance(clipboard_content, str) and clipboard_content.startswith('until:'):
                until_datetime = clipboard_content
                print(f"クリップボードからuntil日時を取得: {until_datetime}")
                
                # until:2025-05-08_16:54:40_JST から 250508 を生成
                try:
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
                        print(f"警告: クリップボードのuntil日時の形式が正しくありません: {until_datetime}")
                        print("期待される形式: until:YYYY-MM-DD_HH:MM:SS_JST")
                        # フォーマットが正しくない場合は現在時刻を使用
                        raise ValueError("Invalid clipboard format")
                except Exception as e:
                    print(f"until日時のパースに失敗: {e}")
                    # エラーが発生した場合は現在時刻を使用
                    now = datetime.now()
                    until_datetime = f"until:{now.strftime('%Y-%m-%d_%H:%M:%S')}_JST"
                    date_str = now.strftime('%Y-%m-%d')
                    print(f"現在時刻のuntil日時を使用: {until_datetime}")
            else:
                # クリップボードに有効な値がない場合は現在時刻を使用
                now = datetime.now()
                until_datetime = f"until:{now.strftime('%Y-%m-%d_%H:%M:%S')}_JST"
                date_str = now.strftime('%Y-%m-%d')
                print(f"現在時刻のuntil日時を使用: {until_datetime}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        if not use_date:
            # --no-date の場合は現在時刻を使用
            now = datetime.now()
            until_datetime = f"until:{now.strftime('%Y-%m-%d_%H:%M:%S')}_JST"
            date_str = now.strftime('%Y-%m-%d')
            print(f"現在時刻のuntil日時を使用: {until_datetime}")
        else:
            print("エラー: 日付の指定が必要です。--no-date オプションを使用するか、日付を指定してください。")
            print(f"指定された日付のuntil日時を使用: {until_datetime}")
            date_str = date_ymd  # 後続の処理で使用するために更新

    # 日付指定ありの場合のみ、日付の形式を確認
    if use_date:
        try:
            # 6桁日付（YYMMDD）形式の場合
            if len(date_str) == 6 and date_str.isdigit():
                year = 2000 + int(date_str[:2])
                month = int(date_str[2:4])
                day = int(date_str[4:6])
                date_obj = datetime(year=year, month=month, day=day)
                date_str = date_obj.strftime('%Y-%m-%d')
            else:
                # YYYY-MM-DD形式の場合
                date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                date_str = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            print("エラー: 無効な日付形式です。YYMMDD または YYYY-MM-DD 形式で指定してください")
            print("例: 250701 または 2025-07-01")
            sys.exit(1)

    # 検索クエリを構築
    if use_date:
        # 日付をYYYY-MM-DD形式に統一
        if len(date_str) == 6 and date_str.isdigit():  # YYMMDD形式の場合
            year = 2000 + int(date_str[:2])
            month = date_str[2:4]
            day = date_str[4:6]
            since_date = f"{year}-{month}-{day}"
        else:
            since_date = date_str  # 既にYYYY-MM-DD形式の場合
            
        # sinceとuntilの形式を統一 (YYYY-MM-DD_HH:MM:SS_JST)
        since_str = f"since:{since_date}_00:00:00_JST"
        
        # untilの形式をチェックして必要に応じて変換
        if until_datetime.startswith('until:') and '_' in until_datetime:
            # 既にuntil:が付いている場合はそのまま使用
            pass
        else:
            # until: が付いていない場合は追加
            until_datetime = f"until:{until_datetime}"
            
        search_query = f"{since_str} {until_datetime} {search_keyword}"
    else:
        search_query = f"{until_datetime} {search_keyword}"
    print(f"検索クエリ: {search_query}")
    print("位置設定を開始します...\n")
    # 各位置を取得
    print("== 位置設定 ==")
    search_box_pos = get_position("検索ボックスの位置(✗ボタンの位置)にマウスを移動してください", test_mode=test_mode)
    extension_button_pos = get_position("ブラウザ拡張ボタンの位置にマウスを移動してください", test_mode=test_mode)

    print("\n=== 自動化開始 ===")
    time.sleep(0.5)

    try:
        # Twitterの検索を実行
        print("Twitterの検索を実行中...")
        navigate_to_twitter_search(search_query, search_box_pos)

        # ページの読み込みを待機
        print("ページの読み込みを待機中...")
        time.sleep(2)

        # ブラウザ拡張ボタンでHTMLをコピー
        print("HTMLをコピー中...")
        html_content = copy_html_with_extension(extension_button_pos)

        if html_content:
            # HTMLをファイルに保存
            filepath = save_html_to_file(html_content, date_str, keyword_type, search_keyword)
            if filepath:
                print(f"HTMLファイルを保存しました: {filepath}")
                return True
            else:
                print("HTMLファイルの保存に失敗しました")
                return False
        else:
            print("エラー: HTMLの取得に失敗しました")
            return False

    except ValueError as ve:
        print("エラー: 無効な日付形式です。YYMMDD または YYYY-MM-DD 形式で指定してください")
        print("例: 250701 または 2025-07-01")
        print(f"詳細: {ve}")
        return False
    except KeyboardInterrupt:
        print("\n処理が中断されました")
        return False
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

if __name__ == "__main__":
    main()
