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
    
    # 抽出コマンド
    extract_parser = subparsers.add_parser('extract', help='指定した日付のツイートを抽出',
                                         usage='%(prog)s [date] [--no-date] [options]')
    extract_parser.add_argument('date', nargs='?', metavar='MMDD', help='抽出する日付 (MMDD形式、--no-date を指定した場合は無視されます)')
    add_common_arguments(extract_parser, include_keyword_type=True)
    extract_parser.add_argument('--no-date', action='store_true', help='最新のHTMLファイルを使用')
    
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
    
    # 共通の引数を追加 (--keyword-type, --search-keyword, --verbose)
    # all_parser には一度だけ追加
    add_common_arguments(all_parser, include_keyword_type=True)
    
    # その他のオプション
    optional.add_argument('--no-date', action='store_true',
                        help='現在の日時を使用（date引数より優先されます）')
    
    # ヘルプオプションを手動で追加
    optional.add_argument('--help', '-h', action='help',
                        help='このヘルプメッセージを表示して終了')
    
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
            parser.error("エラー: 日付を指定するか、--no-date オプションを使用してください")
    
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
    """HTML作成コマンドを実行する"""
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
        date_str = 'latest'  # --no-date の場合は 'latest' を使用
        if hasattr(args, 'verbose') and args.verbose:
            print("日付指定なしで実行します（クリップボードの日付を使用）")

    # カスタムキーワードが指定されている場合は、キーワードタイプをcustomに設定
    keyword_type = 'custom' if hasattr(args, 'search_keyword') and args.search_keyword else args.keyword_type

    # キーワードタイプの検証
    if not validate_keyword_type(keyword_type):
        return False

    if hasattr(args, 'verbose') and args.verbose:
        date_info = 'クリップボードの日付' if no_date else date_str
        print(f"HTML作成を開始します: 日付={date_info}, キーワードタイプ={keyword_type}")
        if hasattr(args, 'search_keyword') and args.search_keyword:
            print(f"カスタム検索キーワード: {args.search_keyword}")

    # HTML作成を実行
    # --no-date の場合は、date_strをNoneに設定して、create_twitter_html_all_main内で
    # クリップボードから日付を取得するようにする
    html_date_str = None if no_date else date_str
    create_twitter_html_all_main(
        date_str=html_date_str,
        search_keyword=args.search_keyword if hasattr(args, 'search_keyword') else None,
        use_date=not no_date,
        keyword_type=keyword_type
    )
    return True


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


def run_extract_command(args):
    """抽出コマンドを実行する"""
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
            
        if hasattr(args, 'verbose') and args.verbose:
            print(f"抽出コマンド引数: {cmd_args}")
            
        # コマンドライン引数を設定
        old_argv = sys.argv
        try:
            sys.argv = cmd_args
            # 抽出を実行
            extract_main()
            return True
        except Exception as e:
            print(f"抽出中にエラーが発生しました: {e}")
            return False
        finally:
            sys.argv = old_argv
    finally:
        sys.argv = old_argv


def run_all_command(args, test_mode=False):
    """全実行コマンドを実行する"""
    # 日付の処理
    if hasattr(args, 'no_date') and args.no_date:
        # 現在の日時を使用（MMDD形式）
        now = datetime.now()
        date_str = now.strftime('%m%d')
        date_full = now.strftime('%Y%m%d')
        args.date = date_str  # args.dateをMMDD形式で更新
    else:
        # 日付の検証
        if not hasattr(args, 'date') or not args.date:
            print("エラー: 日付が指定されていません。MMDD 形式で日付を指定するか、--no-date オプションを使用してください")
            print("例: all 0701 または all --no-date")
            return False
            
        if not validate_date(args.date):
            print("エラー: 無効な日付形式です。MMDD 形式で指定してください")
            return False
            
        date_str = args.date
        date_full = f"2024{date_str}"  # 年は2024年固定

    if not validate_keyword_type(args.keyword_type):
        return False

    if hasattr(args, 'verbose') and args.verbose:
        print(f"全実行を開始します: 日付={date_str} (完全日付: {date_full}), キーワードタイプ={args.keyword_type}")
        if hasattr(args, 'search_keyword') and args.search_keyword:
            print(f"検索キーワード: {args.search_keyword}")

    # 一時的にコマンドライン引数を設定（後方互換性のため）
    old_argv = sys.argv
    try:
        # HTML作成を実行
        from src.create_twitter_html_all import main as create_twitter_html_all_main
        
        # パラメータを設定
        kwargs = {
            'keyword_type': args.keyword_type,
            'use_date': not getattr(args, 'no_date', False),
            'date_override': date_full if getattr(args, 'no_date', False) else None,
            'verbose': getattr(args, 'verbose', False),
            'test_mode': test_mode
        }
        
        if hasattr(args, 'search_keyword') and args.search_keyword:
            kwargs['search_keyword'] = args.search_keyword
            
        if hasattr(args, 'verbose') and args.verbose:
            print(f"HTML作成を実行: date_str={date_str}, kwargs={kwargs}")
            
        # 直接関数を呼び出す
        create_twitter_html_all_main(date_str=date_str, **kwargs)

        if hasattr(args, 'verbose') and args.verbose:
            print("\nHTML作成が完了しました。ツイートの抽出を開始します...")
            
        # 抽出コマンドを実行
        extract_args = argparse.Namespace()
        extract_args.keyword_type = args.keyword_type
        extract_args.verbose = getattr(args, 'verbose', False)
        extract_args.no_date = getattr(args, 'no_date', False)
        if not extract_args.no_date:
            extract_args.date = date_str
            
        if hasattr(args, 'verbose') and args.verbose:
            print(f"抽出コマンドを実行: 日付={date_str}, キーワードタイプ={args.keyword_type}")
            
        # 抽出を実行
        run_extract_command(extract_args)
        
        return True
    finally:
        sys.argv = old_argv


def main():
    """メインエントリーポイント"""
    try:
        # コマンドライン引数を解析
        args = parse_arguments()

        # ログレベルの設定
        if hasattr(args, 'verbose') and args.verbose:
            print("詳細モードで実行します")

        # コマンドを実行
        if args.command == 'all':
            # all コマンドを実行
            if not run_all_command(args):
                sys.exit(1)
        elif args.command == 'html':
            # html コマンドを実行
            if not run_html_command(args):
                sys.exit(1)
        elif args.command == 'merge':
            # merge コマンドを実行
            if not run_merge_command(args):
                sys.exit(1)
        elif args.command == 'extract':
            # extract コマンドを実行
            if not run_extract_command(args):
                sys.exit(1)
        else:
            print("エラー: 不明なコマンドです")
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


if __name__ == "__main__":
    main()
