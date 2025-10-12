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
import json
import re
from datetime import datetime
import argparse
from bs4 import BeautifulSoup

# 設定ファイルをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

def debug_print(message, verbose_flag=False):
    """デバッグメッセージを表示する

    Args:
        message (str): 表示するメッセージ
        verbose_flag (bool): 詳細出力モードの場合にTrue
    """
    if verbose_flag:
        print(f"[DEBUG] {message}")

def ensure_config_dir():
    """設定ディレクトリが存在することを確認し、なければ作成する"""
    os.makedirs(config.CONFIG_DIR, exist_ok=True)

def save_positions(positions):
    """マウスポジションをファイルに保存する"""
    try:
        ensure_config_dir()
        with open(config.POSITION_CONFIG_PATH, 'w') as f:
            json.dump(positions, f, indent=2)
        return True
    except Exception as e:
        print(f"警告: マウスポジションの保存に失敗しました: {e}")
        return False

def load_positions():
    """保存されたマウスポジションを読み込む（リポジトリ内 data/config/positions.json のみ）"""
    try:
        if os.path.exists(config.POSITION_CONFIG_PATH):
            with open(config.POSITION_CONFIG_PATH, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"警告: マウスポジションの読み込みに失敗しました: {e}")

    # デフォルトの位置を返す
    return {
        'search_box': {'x': 0, 'y': 0},
        'extension_button': {'x': 0, 'y': 0}
    }

def get_position(prompt, position_name, test_mode=False, use_saved=False, args=None):
    """指定された位置をユーザーにクリックさせて取得する

    Args:
        prompt (str): ユーザーに表示するプロンプト
        position_name (str): 位置の名前 ('search_box' または 'extension_button')
        test_mode (bool): テストモードの場合はTrue
        use_saved (bool): 保存された位置を使用する場合はTrue
        args: コマンドライン引数

    Returns:
        dict: 位置情報を含む辞書 {'x': x座標, 'y': y座標}
    """
    # テストモードの場合は固定の位置を返す
    if test_mode:
        return {'x': 100, 'y': 200}  # テスト用の固定座標

    # argsから位置情報が指定されている場合はそれを使用
    if hasattr(args, position_name) and getattr(args, position_name) is not None:
        return getattr(args, position_name)

    # 保存された位置を確認
    positions = load_positions()

    # 保存された位置があり、有効な座標の場合
    if use_saved and positions[position_name]['x'] > 0 and positions[position_name]['y'] > 0:
        return {
            'x': positions[position_name]['x'],
            'y': positions[position_name]['y']
        }

    # 新しい位置を取得
    print(f"\n{prompt}")
    input("マウスを移動させて、Enterキーを押すと現在のマウス位置を取得します...")
    position = pyautogui.position()
    print(f"\n取得した座標: x={position.x}, y={position.y}")

    # 位置を保存
    positions = load_positions()
    positions[position_name] = {'x': position.x, 'y': position.y}
    save_positions(positions)
    print("位置を保存しました。")

    return {'x': position.x, 'y': position.y}

def navigate_to_twitter_search(search_query, search_box_pos):
    """Twitterの検索ボックスに検索クエリを入力する

    Args:
        search_query (str): 検索クエリ
        search_box_pos (dict): 検索ボックスと×ボタンの座標 {'x': int, 'y': int}
    """
    # 検索ボックスをクリックしてフォーカス
    pyautogui.click(search_box_pos['x'], search_box_pos['y'])
    time.sleep(0.2)
    # ×ボタンをクリックして検索をクリア
    pyautogui.click(search_box_pos['x'], search_box_pos['y'])
    time.sleep(0.2)

    # 検索クエリをクリップボードにコピーして貼り付け
    pyautogui.click(search_box_pos['x'], search_box_pos['y'])
    pyperclip.copy(search_query)
    time.sleep(0.4)
    pyautogui.hotkey('command', 'v')
    time.sleep(0.2)
    pyautogui.press('enter')
    time.sleep(1)  # 検索結果が表示されるのを待つ

def copy_html_with_extension(extension_button_pos):
    """ブラウザ拡張ボタンを押してHTMLをクリップボードにコピー"""
    x, y = extension_button_pos['x'], extension_button_pos['y']

    # クリック前に少し待機
    time.sleep(0.2)

    # 拡張ボタンをクリック
    pyautogui.click(x, y)
    print(f"拡張ボタンクリック位置: ({x}, {y})")
    time.sleep(0.8)  # コピーが完了するのを待つ

    # クリップボードからHTMLを取得
    html_content = pyperclip.paste()

    # クリップボードからHTMLを取得
    html_content = pyperclip.paste()

    # HTMLの内容を検証
    if not html_content or len(html_content) < 500:
        print("エラー: HTMLの取得に失敗しました。拡張ボタンの位置を確認してください。")
        return None

    return html_content
    """「さらに表示」ボタンがあるツイートの詳細ページを処理

    Args:
        tweets_data: タイムラインから抽出されたツイートデータ
        search_box_pos: 検索ボックスの位置情報
        extension_button_pos: 拡張ボタンの位置情報
        date_str: 日付文字列
        keyword_type: キーワードタイプ

    Returns:
        dict: 詳細ページから取得した完全なテキストデータ {url: text}
    """
    complete_texts = {}

    # 「さらに表示」ボタンがあるツイートのみ処理
    show_more_tweets = [tweet for tweet in tweets_data if tweet.get('has_show_more', False)]

    if not show_more_tweets:
        print("「さらに表示」ボタンのあるツイートはありません")
        return complete_texts

    print(f"「さらに表示」ボタンのあるツイートを {len(show_more_tweets)} 件処理します")

    for tweet in show_more_tweets:
        tweet_url = tweet.get('quote_url')
        if not tweet_url:
            print(f"ツイートURLが見つからないためスキップ: {tweet.get('id', '不明')}")
            continue

        try:
            print(f"\n詳細ページ処理中: {tweet_url}")

            # 新しいタブを開く（Ctrl+T）
            pyautogui.hotkey('command', 't')
            time.sleep(1)

            # URLをクリップボードにコピーして貼り付け
            pyperclip.copy(tweet_url)
            pyautogui.hotkey('command', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(3)  # ページ読み込み待機

            # 詳細ページでHTMLをコピー
            html_content = copy_html_with_extension(extension_button_pos)

            if html_content:
                # HTMLから完全なテキストを抽出
                soup = BeautifulSoup(html_content, 'html.parser')
                text_elements = soup.select('[data-testid="tweetText"] span')
                if text_elements:
                    # 本来のツイート内容は最初の要素のみを使用
                    complete_text = text_elements[0].get_text()
                    complete_text = re.sub(r'\s+', ' ', complete_text).strip()
                    print(f"詳細ページからテキスト取得完了（{len(complete_text)}文字）")
                    complete_texts[tweet_url] = complete_text

                    # 詳細ページのHTMLも保存
                    detail_html_path = save_detail_html_to_file(html_content, tweet_url, date_str, keyword_type)
                    if detail_html_path:
                        print(f"詳細ページのHTMLを保存しました: {detail_html_path}")
                else:
                    print("詳細ページからテキスト要素が見つかりませんでした")
            else:
                print("詳細ページからHTMLの取得に失敗しました")

            # 新しいタブを閉じる（Ctrl+W）
            pyautogui.hotkey('command', 'w')
            time.sleep(0.5)

        except Exception as e:
            print(f"詳細ページ処理中にエラー発生: {e}")
            # エラー時はタブを閉じて続行
            try:
                pyautogui.hotkey('command', 'w')
                time.sleep(0.5)
            except:
                pass

    return complete_texts

def save_detail_html_to_file(html_content, tweet_url, date_str, keyword_type='default'):
    """詳細ページのHTMLコンテンツをファイルに保存する

    Args:
        html_content (str): 保存するHTMLコンテンツ
        tweet_url (str): ツイートURL（ファイル名用に使用）
        date_str (str): 日付文字列
        keyword_type (str): キーワードタイプ（デフォルト: 'default'）

    Returns:
        str: 保存されたファイルのパス、失敗時はNone
    """
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

    # 出力先ディレクトリを決定（input/detailフォルダに保存）
    detail_dir = os.path.join(config.INPUT_FOLDER, 'detail')
    os.makedirs(detail_dir, exist_ok=True)

    # ツイートIDを抽出してファイル名に使用
    tweet_id = tweet_url.split('/')[-1] if '/' in tweet_url else 'unknown'
    filename = f"{yymmdd}_{tweet_id}.html"
    filepath = os.path.join(detail_dir, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    return filepath

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

def main(test_mode=False, date_str=None, search_keyword=None, use_date=True,
         keyword_type='default', verbose=False, date_override=None, continuous=False,
         search_box=None, extension_button=None):

    # デフォルトのargsオブジェクトを作成
    class Args:
        def __init__(self):
            self.continuous = continuous
            self.verbose = verbose
            self.search_box = search_box
            self.extension_button = extension_button

    args = Args()

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
        parser.add_argument('--verbose', '-v', action='store_true',
                          help='詳細な出力を有効化')
        parser.add_argument('--continuous', '-c', action='store_true',
                          help='保存されたマウスポジションを使用して連続実行')

        # コマンドライン引数をパース
        cmd_args = parser.parse_args()

        # 引数から値を設定
        date_str = cmd_args.date
        search_keyword = cmd_args.search_keyword or search_keyword
        keyword_type = cmd_args.keyword_type
        use_date = not cmd_args.no_date
        verbose = cmd_args.verbose or verbose
        continuous = cmd_args.continuous or continuous

        # argsオブジェクトを更新
        args.continuous = continuous
        args.verbose = verbose

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
        parser.add_argument('--continuous', '-c', action='store_true',
                          help='保存されたマウスポジションを使用して連続実行')

        # コマンドライン引数をパース
        cmd_args = parser.parse_args()

        # 引数から値を設定
        date_str = cmd_args.date
        search_keyword = cmd_args.search_keyword
        keyword_type = cmd_args.keyword_type
        use_date = not cmd_args.no_date
        verbose = cmd_args.verbose or verbose
        continuous = cmd_args.continuous or continuous

        # argsオブジェクトを更新
        args.continuous = continuous
        args.verbose = verbose

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
    # まず保存済み位置があるか確認
    positions_for_check = load_positions()
    has_saved_positions = (
        positions_for_check.get('search_box', {}).get('x', 0) > 0 and
        positions_for_check.get('search_box', {}).get('y', 0) > 0 and
        positions_for_check.get('extension_button', {}).get('x', 0) > 0 and
        positions_for_check.get('extension_button', {}).get('y', 0) > 0
    )

    # デフォルトは連続モード指定時は保存位置使用
    use_saved = getattr(args, 'continuous', False) if hasattr(args, 'continuous') else False

    # argsオブジェクトにマウスポジション情報が既に設定されている場合はそれを使用
    args_search_box = getattr(args, 'search_box', None)
    args_extension_button = getattr(args, 'extension_button', None)

    if args_search_box is not None and args_extension_button is not None:
        # argsオブジェクトにマウスポジション情報が設定済みの場合はそれを使用
        search_box_pos = args_search_box
        extension_button_pos = args_extension_button
        print("事前に設定されたマウスポジションを使用します")
    else:
        # マウスポジション設定ロジックを実行（設定フラグは使用せず、毎回確認を求める）
        print("位置設定を開始します...\n")
        # 各位置を取得
        print("== 位置設定 ==")
        # まず保存済み位置があるか確認
        positions_for_check = load_positions()
        has_saved_positions = (
            positions_for_check.get('search_box', {}).get('x', 0) > 0 and
            positions_for_check.get('search_box', {}).get('y', 0) > 0 and
            positions_for_check.get('extension_button', {}).get('x', 0) > 0 and
            positions_for_check.get('extension_button', {}).get('y', 0) > 0
        )

        # 保存済みがある場合のみ、利用可否を対話で確認（毎回確認を求める）
        if has_saved_positions:
            # 保存済み位置がある場合は常に確認を求める
            try:
                if sys.stdin.isatty():
                    ans = input("保存された位置を使用しますか？ [Y/n]: ").strip().lower()
                    if ans in ('n', 'no'):
                        use_saved = False
                    else:
                        # y, Y, または未入力の場合は保存位置を使用
                        use_saved = True
                else:
                    # 非対話（テストなど）では自動で保存位置を使用
                    use_saved = True
            except Exception:
                # 何らかの理由で入力に失敗した場合は安全側（保存位置を使用）
                use_saved = True
        else:
            # 保存がない場合は新規取得
            use_saved = False

        search_box_pos = get_position(
            "検索ボックスの位置(✗ボタンの位置)にマウスを移動してください",
            'search_box',
            test_mode=test_mode,
            use_saved=use_saved,
            args=args
        )

        extension_button_pos = get_position(
            "ブラウザ拡張ボタンの位置にマウスを移動してください",
            'extension_button',
            test_mode=test_mode,
            use_saved=use_saved,
            args=args
        )

        # マウスポジション設定後に設定済みフラグを保存（削除 - 毎回確認するようにする）
        # 設定フラグを保存せず、毎回ユーザーに選択を求めるようにする

    print("\n=== 自動化開始 ===")
    time.sleep(0.2)

    try:
        # Twitterの検索を実行
        print("Twitterの検索を実行中...")
        navigate_to_twitter_search(search_query, search_box_pos)

        # ページの読み込みを待機
        print("ページの読み込みを待機中...")
        time.sleep(0.5)

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
