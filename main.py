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


def parse_arguments():
    """コマンドライン引数を解析する"""
    parser = argparse.ArgumentParser(
        description='Twitter HTML Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""使用例:
  # HTMLファイルを作成
  python main.py --html 250701 --keyword-type chikirin

  # 日付指定なしでHTMLを作成
  python main.py --html --no-date --search-keyword "検索キーワード"

  # ツイートを抽出
  python main.py --extract 250701 -k chikirin

  # テキストファイルを結合
  python main.py --merge --keyword-type chikirin

  # 全実行（HTML作成 + 抽出）
  python main.py --all 250701 -k chikirin

  # 詳細表示モード
  python main.py --html 250701 -v
""")

    # 相互排他的なトップレベルコマンド
    group = parser.add_mutually_exclusive_group(required=True)

    # HTML作成コマンド
    group.add_argument('--html', nargs='?', const=None, metavar='YYMMDD',
                     help='HTMLファイルを作成する（日付指定はオプション）')

    # マージコマンド
    group.add_argument('--merge', action='store_true',
                     help='すべてのテキストファイルをCSVに結合する')

    # 抽出コマンド
    group.add_argument('--extract', metavar='YYMMDD',
                     help='指定した日付のツイートを抽出する')

    # 全実行コマンド
    group.add_argument('--all', nargs='?', const='latest', metavar='YYMMDD',
                     help='HTML作成とツイート抽出を実行する（--no-date と併用可能）')

    # 共通オプション
    parser.add_argument('--keyword-type', '-k', default='default',
                      choices=config.KEYWORD_PREFIX_MAPPING.keys(),
                      help=f'キーワードタイプを指定（デフォルト: default）')

    # HTML作成オプション
    html_group = parser.add_argument_group('HTML作成オプション')
    html_group.add_argument('--no-date', action='store_true',
                          help='日付指定なしでHTMLを作成（--html または --all と併用）')
    html_group.add_argument('--search-keyword',
                          help='カスタム検索キーワードを指定（--html または --all と併用）')

    # 詳細表示オプション
    parser.add_argument('--verbose', '-v', action='store_true',
                      help='詳細なログを表示')

    return parser.parse_args()


def validate_keyword_type(keyword_type):
    """キーワードタイプが有効か検証する"""
    if keyword_type not in config.KEYWORD_PREFIX_MAPPING:
        print(f"エラー: 無効なキーワードタイプ '{keyword_type}'")
        print(f"使用可能なキーワードタイプ: {', '.join(config.KEYWORD_PREFIX_MAPPING.keys())}")
        return False
    return True


def run_html_command(args):
    """HTML作成コマンドを実行する"""
    # 日付の検証（--no-date でない場合）
    if not args.no_date and args.html is not None and not validate_date(args.html):
        print("エラー: 無効な日付形式です。YYMMDD 形式で指定してください")
        print("例: --html 250701")
        return False

    # カスタムキーワードが指定されている場合は、キーワードタイプをcustomに設定
    keyword_type = 'custom' if args.search_keyword else args.keyword_type

    # キーワードタイプの検証
    if not validate_keyword_type(keyword_type):
        return False

    if args.verbose:
        date_info = args.html if not args.no_date else '指定なし'
        print(f"HTML作成を開始します: 日付={date_info}, キーワードタイプ={keyword_type}")
        if args.search_keyword:
            print(f"カスタム検索キーワード: {args.search_keyword}")

    # HTML作成を実行
    create_twitter_html_all_main(
        date_str=args.html if not args.no_date else None,
        search_keyword=args.search_keyword,
        use_date=not args.no_date,
        keyword_type=keyword_type
    )
    return True


def run_merge_command(args):
    """マージコマンドを実行する"""
    if not validate_keyword_type(args.keyword_type):
        return False

    if args.verbose:
        print(f"データを結合します: キーワードタイプ={args.keyword_type}")

    # マージを実行
    merge_all_txt_to_csv(args.keyword_type)
    return True


def run_extract_command(args):
    """抽出コマンドを実行する"""
    # --no-date が指定されているか確認
    no_date = hasattr(args, 'no_date') and args.no_date
    
    # --no-date でない場合は日付を検証
    if not no_date:
        if not hasattr(args, 'extract') or not validate_date(args.extract):
            print("エラー: 無効な日付形式です。YYMMDD 形式で指定するか、--no-date を指定してください")
            print("例1: --extract 250701")
            print("例2: --extract --no-date")
            return False

    if not validate_keyword_type(args.keyword_type):
        return False

    if args.verbose:
        date_info = '最新のHTMLファイル' if no_date else args.extract
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
            sys.argv = [old_argv[0], args.extract, '--keyword-type', args.keyword_type]
            
        if args.verbose:
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
        if not args.all or not validate_date(args.all):
            print("エラー: 無効な日付形式です。YYMMDD 形式で指定するか、--no-date を指定してください")
            print("例1: --all 250701")
            print("例2: --all --no-date")
            return False
        date_str = args.all
    else:
        date_str = 'latest'  # --no-date の場合は 'latest' を使用
        if args.verbose:
            print("日付指定なしで実行します（クリップボードの日付を使用）")

    if not validate_keyword_type(args.keyword_type):
        return False

    if args.verbose:
        date_info = 'クリップボードの日付' if no_date else args.all
        print(f"全実行を開始します: 日付={date_info}, キーワードタイプ={args.keyword_type}")
        if no_date and args.search_keyword:
            print(f"検索キーワード: {args.search_keyword}")

    # 全実行モードでHTML作成を実行
    # --no-date の場合は、date_strをNoneに設定して、create_twitter_html_all_main内で
    # クリップボードから日付を取得するようにする
    html_date_str = None if no_date else date_str
    create_twitter_html_all_main(
        date_str=html_date_str,
        search_keyword=args.search_keyword,
        use_date=not no_date,
        keyword_type=args.keyword_type
    )

    if args.verbose:
        print("HTML作成が完了しました。ツイートの抽出を開始します...")

    # 抽出コマンドを実行するための引数オブジェクトを作成
    class Args:
        def __init__(self):
            # --no-date が指定されている場合は、保存されたHTMLファイルから日付を取得
            if no_date:
                # 最新のHTMLファイルを探す
                import glob
                import os
                list_of_files = glob.glob('data/input/*.html')
                if list_of_files:
                    latest_file = max(list_of_files, key=os.path.getctime)
                    # ファイル名から日付部分を抽出（例: 250826.html から 250826 を抽出）
                    import re
                    match = re.search(r'(\d{6})\.html$', latest_file)
                    if match:
                        self.extract = match.group(1)
                        if args.verbose:
                            print(f"最新のHTMLファイルから日付を取得: {self.extract}")
                    else:
                        print("エラー: 日付形式のファイルが見つかりませんでした")
                        sys.exit(1)
                else:
                    print("エラー: HTMLファイルが見つかりませんでした")
                    sys.exit(1)
            else:
                self.extract = date_str
            self.keyword_type = args.keyword_type
            self.verbose = args.verbose

    # 抽出を実行
    return run_extract_command(Args())


def main():
    """メインエントリーポイント"""
    args = parse_arguments()

    try:
        # ログレベル設定
        if args.verbose:
            print("詳細モードで実行します")

        # 各コマンドを実行
        success = False
        if args.html is not None:
            success = run_html_command(args)
        elif args.merge:
            success = run_merge_command(args)
        elif args.extract is not None:
            success = run_extract_command(args)
        if hasattr(args, 'all'):
            success = run_all_command(args)
        else:
            print("エラー: 無効なコマンドです")
            print("使用可能なコマンド: --html, --merge, --extract, --all")
            sys.exit(1)

        if not success:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n処理を中断しました")
        sys.exit(1)
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"エラー: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
