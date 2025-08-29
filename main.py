#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter HTML Extractor メインプログラム

このスクリプトは、TwitterのHTMLファイルからツイートを抽出し、CSVファイルに保存します。

使い方:
  python main.py --html 250803 [--keyword-type TYPE] [--search-keyword KEYWORD] [--no-date] [--verbose]
  python main.py --merge [--keyword-type TYPE] [--verbose]
  python main.py --extract DATE [--keyword-type TYPE] [--verbose]
  python main.py --all DATE [--keyword-type TYPE] [--verbose]

例:
  # HTML作成
  python main.py --html 250803
  python main.py --html 250803 --keyword-type chikirin
  python main.py --html --no-date --keyword-type thai
"""

import os
import sys
import argparse
from datetime import datetime

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定ファイルのインポート
import config
from src.extract_tweets_from_html import main as extract_main
from src.merge_all_txt_to_csv import merge_all_txt_to_csv
from src.create_twitter_html_all import main as create_twitter_html_all_main


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
    import config
    
    # メインパーサーを作成
    parser = argparse.ArgumentParser(
        description='Twitter HTML Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    
    # メインコマンドグループ（相互排他）
    subparsers = parser.add_subparsers(dest='command', help='サブコマンド')
    
    # HTMLコマンド
    html_parser = subparsers.add_parser('html', help='HTMLファイルを作成')
    html_parser.add_argument('date', nargs='?', metavar='YYMMDD',
                          help='日付（オプション）')
    
    # マージコマンド
    merge_parser = subparsers.add_parser('merge', help='すべてのテキストファイルをCSVに結合')
    
    # 抽出コマンド
    extract_parser = subparsers.add_parser('extract', help='指定した日付のツイートを抽出')
    extract_parser.add_argument('date', metavar='YYMMDD', help='抽出する日付')
    
    # 全実行コマンド
    all_parser = subparsers.add_parser('all', help='HTML作成とツイート抽出を実行')
    all_parser.add_argument('date', nargs='?', metavar='YYMMDD',
                          help='日付（オプション）')
    
    # 共通オプション
    for p in [html_parser, merge_parser, extract_parser, all_parser]:
        p.add_argument('--keyword-type', '-k',
                     default='default',
                     choices=config.KEYWORD_PREFIX_MAPPING.keys(),
                     help='キーワードタイプを指定（デフォルト: %(default)s）')
        p.add_argument('--no-date', action='store_true',
                     help='日付指定なしで実行')
        p.add_argument('--search-keyword',
                     help='カスタム検索キーワードを指定')
        p.add_argument('--verbose', '-v', action='store_true',
                     help='詳細な出力を有効化')
    
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
        
    return parser.parse_args(args)


def validate_keyword_type(keyword_type):
    """キーワードタイプが有効か検証する"""
    if keyword_type not in config.KEYWORD_PREFIX_MAPPING:
        print(f"エラー: 無効なキーワードタイプ '{keyword_type}'")
        print(f"使用可能なキーワードタイプ: {', '.join(config.KEYWORD_PREFIX_MAPPING.keys())}")
        return False
    return True


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
    # --no-date が指定されているか確認
    no_date = hasattr(args, 'no_date') and args.no_date
    
    # --no-date でない場合は日付を検証
    if not no_date:
        if not hasattr(args, 'date') or not args.date or not validate_date(args.date):
            print("エラー: 無効な日付形式です。YYMMDD 形式で指定するか、--no-date を指定してください")
            print("例1: extract 250701")
            print("例2: extract --no-date")
            return False
        date_str = args.date
    else:
        date_str = 'latest'  # --no-date の場合は 'latest' を使用
        if hasattr(args, 'verbose') and args.verbose:
            print("最新のHTMLファイルから抽出します")

    if not validate_keyword_type(args.keyword_type):
        return False

    if hasattr(args, 'verbose') and args.verbose:
        date_info = '最新のHTMLファイル' if no_date else date_str
        print(f"ツイートを抽出します: 日付={date_info}, キーワードタイプ={args.keyword_type}")

    # 一時的にコマンドライン引数を設定（後方互換性のため）
    old_argv = sys.argv
    try:
        if no_date:
            # --no-date の場合は、最新のHTMLファイルを検索
            import glob
            import os
            list_of_files = glob.glob('data/input/*.html')
            if not list_of_files:
                print("エラー: 抽出するHTMLファイルが見つかりません")
                return False
            latest_file = max(list_of_files, key=os.path.getctime)
            # ファイル名から日付部分を抽出（例: 250826.html から 250826 を抽出）
            import re
            match = re.search(r'(\d{6})\.html$', latest_file)
            if not match:
                print("エラー: 日付形式のファイルが見つかりませんでした")
                return False
            date_str = match.group(1)
            sys.argv = [old_argv[0], date_str, '--keyword-type', args.keyword_type]
        else:
            sys.argv = [old_argv[0], date_str, '--keyword-type', args.keyword_type]
            
        if hasattr(args, 'verbose') and args.verbose:
            sys.argv.append('--verbose')

        # 抽出を実行
        extract_main()
        return True
    finally:
        sys.argv = old_argv


def run_all_command(args):
    """全実行コマンドを実行する"""
    # --no-date が指定されているか確認
    no_date = hasattr(args, 'no_date') and args.no_date
    
    # 日付の検証（--no-date でない場合）
    if not no_date:
        if not hasattr(args, 'date') or not args.date or not validate_date(args.date):
            print("エラー: 無効な日付形式です。YYMMDD 形式で指定するか、--no-date を指定してください")
            print("例1: all 250701")
            print("例2: all --no-date")
            return False
        date_str = args.date
    else:
        date_str = 'latest'  # --no-date の場合は 'latest' を使用
        if hasattr(args, 'verbose') and args.verbose:
            print("日付指定なしで実行します（クリップボードの日付を使用）")

    if not validate_keyword_type(args.keyword_type):
        return False

    if hasattr(args, 'verbose') and args.verbose:
        date_info = 'クリップボードの日付' if no_date else date_str
        print(f"全実行を開始します: 日付={date_info}, キーワードタイプ={args.keyword_type}")
        if hasattr(args, 'search_keyword') and args.search_keyword:
            print(f"検索キーワード: {args.search_keyword}")

    # 一時的にコマンドライン引数を設定（後方互換性のため）
    old_argv = sys.argv
    try:
        # HTML作成を実行
        html_argv = [old_argv[0]]
        if no_date:
            html_argv.extend(['--no-date'])
        else:
            html_argv.append(date_str)
            
        html_argv.extend(['--keyword-type', args.keyword_type])
            
        if hasattr(args, 'search_keyword') and args.search_keyword:
            html_argv.extend(['--search-keyword', args.search_keyword])
            
        if hasattr(args, 'verbose') and args.verbose:
            html_argv.append('--verbose')
            
        # HTML作成を実行
        from src.create_twitter_html_all import main as create_twitter_html_all_main
        sys.argv = html_argv
        if hasattr(args, 'verbose') and args.verbose:
            print(f"HTML作成を実行: {' '.join(sys.argv)}")
        create_twitter_html_all_main()

        if hasattr(args, 'verbose') and args.verbose:
            print("\nHTML作成が完了しました。ツイートの抽出を開始します...")
            
        # 抽出コマンドを実行
        if no_date:
            # --no-date の場合は、最新のHTMLファイルを検索
            import glob
            import os
            list_of_files = glob.glob('data/input/*.html')
            if not list_of_files:
                print("エラー: 抽出するHTMLファイルが見つかりません")
                return False
            latest_file = max(list_of_files, key=os.path.getctime)
            # ファイル名から日付部分を抽出（例: 250826.html から 250826 を抽出）
            import re
            match = re.search(r'(\d{6})\.html$', latest_file)
            if not match:
                print("エラー: 日付形式のファイルが見つかりませんでした")
                return False
            date_str = match.group(1)
            
        # 抽出用の引数を設定
        extract_argv = [old_argv[0], date_str, '--keyword-type', args.keyword_type]
        if hasattr(args, 'verbose') and args.verbose:
            extract_argv.append('--verbose')
            
        # 抽出を実行
        from src.extract_tweets_from_html import main as extract_main
        sys.argv = extract_argv
        if hasattr(args, 'verbose') and args.verbose:
            print(f"抽出を実行: {' '.join(sys.argv)}")
        extract_main()
        
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
