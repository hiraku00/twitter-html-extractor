#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter HTML Extractor メインプログラム

このスクリプトは、TwitterのHTMLファイルからツイートを抽出し、CSVファイルに保存します。

使い方:
  python main.py html 250803 [--keyword-type TYPE] [--search-keyword KEYWORD] [--no-date] [--verbose]
  python main.py merge [--keyword-type TYPE] [--verbose]
  python main.py extract DATE [--keyword-type TYPE] [--verbose]
  python main.py all DATE [--keyword-type TYPE] [--verbose]

例:
  # HTML作成
  python main.py html 250803
  python main.py html 250803 --keyword-type chikirin
  python main.py html --no-date --keyword-type thai
"""

import os
import sys
import importlib
import argparse
from datetime import datetime, timedelta
from pathlib import Path

# カスタムのArgumentParserクラスを定義
class CustomArgumentParser(argparse.ArgumentParser):
    def _get_value(self, action, arg_string):
        # キーワードタイプの検証を無効化
        if action.dest == 'keyword_type':
            return arg_string
        return super()._get_value(action, arg_string)
    
    def add_argument(self, *args, **kwargs):
        # キーワードタイプの引数に対しては、choicesを無効化
        if 'dest' in kwargs and kwargs['dest'] == 'keyword_type':
            kwargs.pop('choices', None)
        
        # --no-date オプションの処理を追加
        if '--no-date' in args:
            kwargs['required'] = False
            
        return super().add_argument(*args, **kwargs)

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定ファイルのインポート
import config
from src.extract_tweets_from_html import main as extract_main
from src.merge_all_txt_to_csv import merge_all_txt_to_csv
from src.create_twitter_html_all import main as create_twitter_html_all_main

class StoreKeywordAction(argparse.Action):
    """カスタムアクションクラス：キーワードタイプを動的に検証"""
    def __init__(self, option_strings, dest, **kwargs):
        # choices パラメータを削除
        if 'choices' in kwargs:
            del kwargs['choices']
        super().__init__(option_strings, dest, **kwargs)
    
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            # 設定を再読み込み
            importlib.reload(config)
            current_choices = list(config.KEYWORD_PREFIX_MAPPING.keys())
            
            # デバッグ用に現在の選択肢を出力
            print(f"DEBUG: Reloaded config in StoreKeywordAction")
            print(f"DEBUG: Available choices in action: {current_choices}")
            
            # キーワードタイプを検証
            if values not in current_choices:
                raise argparse.ArgumentError(
                    self,
                    f"無効なキーワードタイプ: '{values}'. 有効な選択肢: {', '.join(map(repr, current_choices))}"
                )
            setattr(namespace, self.dest, values)
        except Exception as e:
            print(f"ERROR in StoreKeywordAction: {str(e)}")
            raise

def reload_config():
    """設定ファイルを再読み込みする"""
    importlib.reload(config)
    return config


def validate_date(date_str):
    """日付文字列が有効か検証する"""
    if not date_str:
        return False

    # YYMMDD形式を検証
    if len(date_str) == 6 and date_str.isdigit():
        try:
            # 20XX年を仮定して日付をパース
            year = 2000 + int(date_str[:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            datetime(year=year, month=month, day=day)
            return True
        except ValueError:
            return False
    # YYYY-MM-DD形式もサポート
    elif len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    return False



def parse_arguments(args=None):
    """コマンドライン引数を解析する
    
    Args:
        args: コマンドライン引数のリスト（デフォルト: Noneの場合はsys.argv[1:]が使用される）
    """
    # 設定を再読み込み
    config = reload_config()
    
    # キーワードタイプの選択肢を動的に取得
    keyword_choices = sorted(list(config.KEYWORD_PREFIX_MAPPING.keys()))
    choices_str = ', '.join(keyword_choices)
    
    # デバッグ情報は削除
    
    # メインパーサーを作成
    parser = CustomArgumentParser(
        description='Twitter HTML Extractor',
        add_help=False
    )
    
    # メインコマンドグループ（相互排他）
    subparsers = parser.add_subparsers(dest='command', title='サブコマンド')
    subparsers.required = True
    
    # カスタムアクションを定義
    class CustomStoreKeywordAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # テスト環境ではリロードをスキップ
            if not hasattr(self, '_is_test'):
                importlib.reload(config)
            current_choices = list(config.KEYWORD_PREFIX_MAPPING.keys())
            if values not in current_choices:
                raise argparse.ArgumentError(self, f"無効なキーワードタイプ: '{values}'. 有効な選択肢: {', '.join(map(repr, current_choices))}")
            setattr(namespace, self.dest, values)
    
    # ベースの引数を追加する関数
    def add_common_arguments(parser, include_keyword_type=True):
        if include_keyword_type and '--keyword-type' not in {a.dest for a in parser._actions}:
            parser.add_argument('--keyword-type', '-k',
                             default='default',
                             dest='keyword_type',
                             action=CustomStoreKeywordAction,
                             help='キーワードタイプを指定（デフォルト: default）')
        if '--search-keyword' not in {a.dest for a in parser._actions}:
            parser.add_argument('--search-keyword',
                             help='カスタム検索キーワードを指定')
        if '--verbose' not in {a.dest for a in parser._actions}:
            parser.add_argument('--verbose', '-v', action='store_true',
                             help='詳細な出力を有効化')
        if '--continuous' not in {a.dest for a in parser._actions}:
            parser.add_argument('--continuous', '-c', type=int, metavar='COUNT',
                      help='指定した回数だけ連続実行します')
    
    # HTMLコマンド
    html_parser = subparsers.add_parser('html', help='HTMLファイルを作成',
                                      usage='%(prog)s [date] [--no-date] [options]')
    html_parser.add_argument('date', nargs='?', help='日付 (YYMMDD形式、--no-date を指定した場合は無視されます)')
    # 共通の引数を追加 (--keyword-type, --search-keyword, --verbose)
    add_common_arguments(html_parser, include_keyword_type=True)
    html_parser.add_argument('--no-date', action='store_true', help='現在の日時を使用')
    html_parser.set_defaults(func=run_html_command)
    
    # マージコマンド
    merge_parser = subparsers.add_parser('merge', help='すべてのテキストファイルをCSVに結合')
    add_common_arguments(merge_parser, include_keyword_type=True)
    merge_parser.set_defaults(func=run_merge_command)
    
    # 抽出コマンド
    extract_parser = subparsers.add_parser('extract', help='指定した日付のツイートを抽出',
                                         usage='%(prog)s [date] [--no-date] [options]')
    extract_parser.add_argument('date', nargs='?', metavar='MMDD', help='抽出する日付 (MMDD形式、--no-date を指定した場合は無視されます)')
    add_common_arguments(extract_parser, include_keyword_type=True)
    extract_parser.add_argument('--no-date', action='store_true', help='最新のHTMLファイルを使用')
    extract_parser.set_defaults(func=run_extract_command)
    
    # 全実行コマンド
    all_parser = subparsers.add_parser('all', help='HTML作成とツイート抽出を実行',
                                     usage='%(prog)s [date] [--no-date] [options]',
                                     add_help=False)
    
    # 必須の引数グループ
    required = all_parser.add_argument_group('必須引数')
    
    # オプションの引数グループ
    optional = all_parser.add_argument_group('オプション')
    
    # 日付引数（オプショナル）
    required.add_argument('date', nargs='?', help='日付 (YYMMDD形式)')
    
    # 共通の引数を追加 (--keyword-type, --search-keyword, --verbose, --continuous)
    add_common_arguments(all_parser, include_keyword_type=True)
    
    # その他のオプション
    optional.add_argument('--no-date', action='store_true',
                        help='現在の日時を使用（date引数より優先されます）')
    
    # ヘルプオプションを手動で追加
    optional.add_argument('--help', '-h', action='help',
                        help='このヘルプメッセージを表示して終了')
    
    # continuousオプションが指定されているか確認
    if '--continuous' in sys.argv or '-c' in sys.argv:
        all_parser.set_defaults(func=run_continuous_mode)
    else:
        all_parser.set_defaults(func=run_all_command)
    
    # 他のパーサーに共通の引数を追加（all_parserは除外）
    for p in [html_parser, merge_parser, extract_parser]:
        p._optionals.title = 'オプション'
    
    # ヘルプオプションを追加
    parser.add_argument('--help', '-h', action='help',
                      help='このヘルプメッセージを表示して終了')
    
    # カスタムヘルプメッセージ
    parser.epilog = """
使用例:
  # HTML作成
  python main.py html 250701 --keyword-type chikirin

  # 日付指定なしでHTML作成
  python main.py html --no-date --search-keyword "検索キーワード"

  # ツイート抽出
  python main.py extract 250701 -k chikirin

  # ファイル結合
  python main.py merge --keyword-type chikirin

  # 一括実行（作成 + 抽出）
  python main.py all 250827 -k chikirin
"""
    
    # 引数をパース
    if args is None:
        args = sys.argv[1:]
    
    # サブコマンドが指定されていない場合はヘルプを表示
    if not args or args[0].startswith('-'):
        parser.print_help()
        sys.exit(1)
    
    # 引数をパース
    # まず--no-dateオプションがあるか確認
    no_date = '--no-date' in args
    if no_date:
        args.remove('--no-date')
    
    # 引数をパース
    parsed_args = parser.parse_args(args)
    
    # --no-dateフラグを設定
    if hasattr(parsed_args, 'no_date'):
        parsed_args.no_date = no_date
    
    # allコマンドで--no-dateが指定されている場合、dateをNoneに設定
    if parsed_args.command == 'all' and no_date:
        parsed_args.date = None
    
    # 日付の検証
    if parsed_args.command in ['html', 'all'] and not no_date:
        if not hasattr(parsed_args, 'date') or parsed_args.date is None:
            # 日付未指定の場合はJSTで前日をデフォルト設定 (YYMMDD)
            try:
                # JSTはUTC+9。日付のみ必要なため、素直にUTCに+9時間してからdate()を取得
                now_jst = datetime.utcnow() + timedelta(hours=9)
                yesterday_jst = now_jst.date() - timedelta(days=1)
                auto_date = yesterday_jst.strftime("%y%m%d")
                parsed_args.date = auto_date
                # 詳細表示が有効なら通知
                if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
                    print(f"INFO: 日付未指定のため前日を自動設定しました: {parsed_args.date} (JST)")
            except Exception:
                # フォールバック（ローカル時間の前日）
                local_yesterday = (datetime.now() - timedelta(days=1)).strftime("%y%m%d")
                parsed_args.date = local_yesterday
                if hasattr(parsed_args, 'verbose') and parsed_args.verbose:
                    print(f"INFO: 日付未指定のため前日(ローカル)を自動設定しました: {parsed_args.date}")
    
    # キーワードタイプを検証
    if not validate_keyword_type(parsed_args.keyword_type):
        print(f"エラー: 無効なキーワードタイプです。使用可能な選択肢: {', '.join(config.KEYWORD_PREFIX_MAPPING.keys())}")
        sys.exit(1)
        
    return parsed_args


def validate_keyword_type(keyword_type):
    """キーワードタイプが有効か検証する"""
    try:
        # 設定を再読み込み
        config = reload_config()
        current_choices = list(config.KEYWORD_PREFIX_MAPPING.keys())
        return keyword_type in current_choices
    except Exception as e:
        print(f"エラー: キーワードタイプの検証中にエラーが発生しました: {str(e)}")
        return False


def run_html_command(args):
    """HTML作成コマンドを実行する
    
    Args:
        args: コマンドライン引数
        
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    try:
        # --no-date が指定されているか確認
        no_date = hasattr(args, 'no_date') and args.no_date
        
        # 日付の検証（--no-date でない場合）
        if not no_date:
            if not hasattr(args, 'date') or not args.date or not validate_date(args.date):
                print("エラー: 無効な日付形式です。YYMMDD 形式で指定するか、--no-date を指定してください")
                print("例1: html 250701")
                print("例2: html --no-date")
                return False
            date_str = args.date
        else:
            date_str = None

        # キーワードタイプの検証
        if not validate_keyword_type(args.keyword_type):
            return False

        # キーワードタイプを取得
        keyword_type = args.keyword_type
        
        # 検索キーワードが指定されている場合は表示
        if hasattr(args, 'search_keyword') and args.search_keyword:
            if hasattr(args, 'verbose') and args.verbose:
                print(f"カスタム検索キーワード: {args.search_keyword}")

        # HTML作成を実行
        # --no-date の場合は、date_strをNoneに設定して、create_twitter_html_all_main内で
        # クリップボードから日付を取得するようにする
        html_date_str = None if no_date else date_str
        
        # 必要な引数を準備
        from src.create_twitter_html_all import main as create_twitter_html_all_main
        
        # 引数を渡してHTML作成を実行
        kwargs = {
            'date_str': html_date_str,
            'search_keyword': args.search_keyword,
            'keyword_type': keyword_type,
            'verbose': args.verbose if hasattr(args, 'verbose') else False,
            'use_date': not no_date,  # no_dateの逆を渡す
            'test_mode': False,
            'date_override': getattr(args, 'date_override', None),  # date_overrideがあれば使用
            'continuous': False,
            'search_box': getattr(args, 'search_box', None),
            'extension_button': getattr(args, 'extension_button', None)
        }
            
        create_twitter_html_all_main(**kwargs)
        return True
    except Exception as e:
        print(f"HTML作成中にエラーが発生しました: {e}")
        if hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return False


def run_merge_command(args):
    """マージコマンドを実行する"""
    if not validate_keyword_type(args.keyword_type):
        return False

    if hasattr(args, 'verbose') and args.verbose:
        print(f"データを結合します: キーワードタイプ={args.keyword_type}")

    # マージを実行
    merge_all_txt_to_csv(args.keyword_type)
    return True
    return True


def run_extract_command(args, test_mode=False):
    """抽出コマンドを実行する
    
    Args:
        args: コマンドライン引数
        test_mode: テストモードかどうか
        
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    # --no-date が指定されていない場合のみ日付を検証
    if not getattr(args, 'no_date', False):
        if not hasattr(args, 'date') or not args.date or not validate_date(args.date):
            print("エラー: 無効な日付形式です。MMDD 形式で指定するか、--no-date オプションを使用してください")
            print("例: extract 0701 または extract --no-date")
            return False
        date_str = args.date
    else:
        date_str = None

    if not validate_keyword_type(args.keyword_type):
        return False

    if hasattr(args, 'verbose') and args.verbose:
        print(f"ツイートを抽出します: 日付={date_str}, キーワードタイプ={args.keyword_type}")

    # 一時的にコマンドライン引数を設定（後方互換性のため）
    old_argv = sys.argv
    try:
        # 抽出を実行
        from src.extract_tweets_from_html import main as extract_main
        
        # 抽出コマンドの引数を設定
        cmd_args = ['extract_tweets_from_html.py']
        
        # 日付の指定方法を決定
        if hasattr(args, 'no_date') and args.no_date:
            # --no-date が指定されている場合は日付を指定しない
            cmd_args.append('--no-date')
        elif date_str:
            # 通常は日付を指定
            cmd_args.append(date_str)
        
        # キーワードタイプを指定
        if hasattr(args, 'keyword_type') and args.keyword_type:
            cmd_args.extend(['--keyword-type', args.keyword_type])
            
        # 詳細出力を指定
        if hasattr(args, 'verbose') and args.verbose:
            cmd_args.append('--verbose')
            
        old_argv = sys.argv
        try:
            # 抽出コマンドを実行
            if not test_mode:
                print("\n=== 抽出コマンドを実行します ===")
                
            # 抽出を実行
            from src.extract_tweets_from_html import main as extract_main
            
            # 抽出コマンドの引数を設定
            cmd_args = ['extract_tweets_from_html.py']
            
            # 日付の指定方法を決定
            if hasattr(args, 'no_date') and args.no_date:
                # --no-date が指定されている場合は日付を指定しない
                cmd_args.append('--no-date')
            elif date_str:
                # 通常は日付を指定
                cmd_args.append(date_str)
            
            # キーワードタイプを指定
            if hasattr(args, 'keyword_type') and args.keyword_type:
                cmd_args.extend(['--keyword-type', args.keyword_type])
                
            # 詳細出力を指定
            if hasattr(args, 'verbose') and args.verbose:
                cmd_args.append('--verbose')
                
            # 抽出を実行
            sys.argv = cmd_args
            extract_success = extract_main()
            
            if not extract_success:
                error_msg = "抽出に失敗しました"
                print(error_msg)
                return False

            if hasattr(args, 'verbose') and args.verbose:
                print("\n抽出が完了しました。")
                
            return True
        finally:
            sys.argv = old_argv
    except Exception as e:
        error_msg = f"エラー: コマンドの実行中にエラーが発生しました: {e}"
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        print(error_msg)
        return False
    except KeyboardInterrupt:
        print("\n処理を中断しました")
        sys.exit(1)
    except Exception as e:
        if 'args' in locals() and hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"エラー: {str(e)}")
        sys.exit(1)


def main():
    """メインエントリーポイント"""
    try:
        # コマンドライン引数を解析
        args = parse_arguments()
        
        # コマンドを実行
        if hasattr(args, 'func'):
            result = args.func(args)
            if result is not None and not result:
                sys.exit(1)
        else:
            print("エラー: 無効なコマンドです")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n処理を中断しました")
        sys.exit(1)
    except Exception as e:
        if 'args' in locals() and hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"エラー: {str(e)}")
        sys.exit(1)

def run_all_command(args, test_mode=False):
    """全てのコマンドを順番に実行する
    
    Args:
        args: コマンドライン引数
        test_mode: テストモードかどうか
        
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    # --continuous オプションが指定されている場合は連続実行モードを呼び出す
    if hasattr(args, 'continuous') and args.continuous:
        return run_continuous_mode(args, test_mode)
        
    try:
        # HTML作成
        if not run_html_command(args):
            print("HTMLの作成に失敗しました")
            return False
            
        # 抽出
        if not run_extract_command(args):
            print("ツイートの抽出に失敗しました")
            return False
            
        return True
    except Exception as e:
        error_msg = f"ツイートの抽出中にエラーが発生しました: {str(e)}"
        if hasattr(args, 'verbose') and args.verbose:
            print(error_msg)
            import traceback
            traceback.print_exc()
        return False

def run_continuous_mode(args, test_mode=False, command='all'):
    """連続実行モードを実行する
    
    Args:
        args: コマンドライン引数
        test_mode: テストモードかどうか
        command: 実行するコマンド ('all' または 'extract')
        
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    import time
    from datetime import datetime
    
    # テストモードの場合は、pyautoguiやinputをモック
    if test_mode:
        import types
        sys.modules['pyautogui'] = types.SimpleNamespace(position=lambda: types.SimpleNamespace(x=0, y=0))
        global input
        original_input = input
        input = lambda _: None
    
    try:
        print(f"連続実行モードを開始します (最大{args.continuous}回)")
        success_count = 0
        
        # テストモードでない場合のみ、位置情報の入力を求める
        search_box_pos = getattr(args, 'search_box', {'x': 0, 'y': 0})
        extension_button_pos = getattr(args, 'extension_button', {'x': 0, 'y': 0})
        
        if not test_mode:
            try:
                import pyautogui
                from src.create_twitter_html_all import load_positions, save_positions
                
                # 保存された位置を確認
                positions = load_positions()
                use_saved = True
                
                # 保存された位置があり、有効な座標の場合は自動的に使用
                if (positions.get('search_box', {}).get('x', 0) > 0 and 
                    positions.get('search_box', {}).get('y', 0) > 0 and
                    positions.get('extension_button', {}).get('x', 0) > 0 and 
                    positions.get('extension_button', {}).get('y', 0) > 0):
                    search_box_pos = positions['search_box']
                    extension_button_pos = positions['extension_button']
                else:
                    use_saved = False
                    print("保存されている位置情報が見つかりませんでした。新しい位置を設定します。")
                    
                    # 位置情報を取得
                    print("\n=== 位置設定 ===")
                    print("検索ボックス(✗ボタンの位置)にマウスを移動させて、Enterキーを押してください...")
                    input("準備ができたらEnterキーを押してください...")
                    search_box_pos = {'x': pyautogui.position().x, 'y': pyautogui.position().y}
                    print(f"検索ボックスの位置を記録しました: {search_box_pos}")
                    
                    print("\nブラウザ拡張ボタンにマウスを移動させて、Enterキーを押してください...")
                    input("準備ができたらEnterキーを押してください...")
                    extension_button_pos = {'x': pyautogui.position().x, 'y': pyautogui.position().y}
                    print(f"拡張ボタンの位置を記録しました: {extension_button_pos}")
                    
                    # 位置を保存
                    positions = {
                        'search_box': search_box_pos,
                        'extension_button': extension_button_pos
                    }
                    save_positions(positions)
                    
                # マウス位置をargsに設定
                args.search_box = search_box_pos
                args.extension_button = extension_button_pos
                
            except ImportError:
                print("警告: pyautoguiが利用できないため、デフォルトの位置情報を使用します")
            except Exception as e:
                print(f"警告: 位置情報の取得中にエラーが発生しました: {e}")
        
        print("\n=== 自動化開始 ===")
        
        # 現在の日時を初期値として設定
        current_until = datetime.now()
        
        for i in range(args.continuous):
            try:
                if not test_mode or i == 0:  # テストモードでは1回だけ実行
                    print(f"\n--- 実行 {i+1}/{args.continuous} ---")
                    
                    # 前回のuntil日時を取得（初回は現在時刻）
                    until_date = current_until.strftime("%Y-%m-%d")
                    until_time = current_until.strftime("%H:%M:%S")
                    until_str = f"until:{until_date}_{until_time}_JST"
                    print(f"検索範囲: {until_str}")
                    
                    # 新しい引数オブジェクトを作成
                    new_args = argparse.Namespace(
                        command=command,
                        date=args.date,
                        no_date=args.no_date,
                        keyword_type=args.keyword_type,
                        search_keyword=args.search_keyword,
                        verbose=args.verbose,
                        continuous=True,  # 連続実行モードであることを示す
                        until=until_str,   # 前回のuntil日時を設定
                        date_override=until_date,  # 日付部分のみをdate_overrideとして渡す
                        search_box=search_box_pos,
                        extension_button=extension_button_pos
                    )
                    
                    # 各コマンドを個別に実行
                    success = True
                    
                    # 1. HTML作成
                    if success and command == 'all':
                        print("\n=== HTML作成 ===")
                        success = run_html_command(new_args)
                        if not success:
                            print("HTMLの作成に失敗しました")
                    
                    # 2. ツイート抽出
                    if success:
                        print("\n=== ツイート抽出 ===")
                        success = run_extract_command(new_args, test_mode=test_mode)
                        if not success:
                            print("ツイートの抽出に失敗しました")
                    
                    if success:
                        success_count += 1
                        print(f"\n成功: 現在の成功回数 {success_count}/{args.continuous}回")
                    else:
                        print(f"\n失敗: 現在の成功回数 {success_count}/{args.continuous}回")
                        
            except KeyboardInterrupt:
                print("\n処理が中断されました")
                break
            except Exception as e:
                print(f"\nエラーが発生しました: {e}")
                if hasattr(args, 'verbose') and args.verbose:
                    import traceback
                    traceback.print_exc()
        
        print(f"\n連続実行を完了しました (成功: {success_count}/{args.continuous}回)")
        return success_count > 0
        
    finally:
        # 元のinput関数に戻す
        if test_mode and 'original_input' in locals():
            input = original_input

# モジュールレベルの関数として公開
__all__ = ['run_all_command', 'run_continuous_mode', 'run_html_command', 
           'run_extract_command', 'run_merge_command', 'parse_arguments',
           'validate_date', 'validate_keyword_type']

if __name__ == "__main__":
    main()
