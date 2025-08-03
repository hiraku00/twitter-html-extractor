#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Twitter HTML Extractor メインプログラム

このスクリプトは、TwitterのHTMLファイルからツイートを抽出し、CSVファイルに保存します。

使い方:
  python main.py --html 250803 [--keyword-type TYPE] [--search-keyword KEYWORD] [--no-date] [--verbose]
  python main.py --merge [--keyword-type TYPE] [--verbose]
  python main.py --extract DATE [--keyword-type TYPE] [--verbose]
  python main.py --auto DATE [--keyword-type TYPE] [--verbose]

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
from src.create_twitter_html_auto import main as create_twitter_html_auto_main


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
  
  # 自動実行（HTML作成 + 抽出）
  python main.py --auto 250701 -k chikirin
  
  # 詳細表示モード
  python main.py --html 250701 -v
""")
    
    # 相互排他のトップレベルコマンド
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
    
    # 自動実行コマンド
    group.add_argument('--auto', metavar='YYMMDD',
                     help='HTML作成とツイート抽出を自動実行する')
    
    # 共通オプション
    parser.add_argument('--keyword-type', '-k', default='default',
                      choices=config.KEYWORD_PREFIX_MAPPING.keys(),
                      help=f'キーワードタイプを指定（デフォルト: default）')
    
    # HTML作成オプション
    html_group = parser.add_argument_group('HTML作成オプション')
    html_group.add_argument('--no-date', action='store_true',
                          help='日付指定なしでHTMLを作成（--html と併用）')
    html_group.add_argument('--search-keyword',
                          help='カスタム検索キーワードを指定（--html と併用）')
    
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
    create_twitter_html_auto_main(
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
    # 日付の検証
    if not validate_date(args.extract):
        print("エラー: 無効な日付形式です。YYMMDD 形式で指定してください")
        print("例: --extract 250701")
        return False
    
    if not validate_keyword_type(args.keyword_type):
        return False
    
    if args.verbose:
        print(f"ツイートを抽出します: 日付={args.extract}, キーワードタイプ={args.keyword_type}")
    
    # 一時的にコマンドライン引数を設定（後方互換性のため）
    old_argv = sys.argv
    try:
        sys.argv = [old_argv[0], args.extract, '--keyword-type', args.keyword_type]
        if args.verbose:
            sys.argv.append('--verbose')
        
        # 抽出を実行
        extract_main()
        return True
    finally:
        sys.argv = old_argv


def run_auto_command(args):
    """自動実行コマンドを実行する"""
    # 日付の検証
    if not validate_date(args.auto):
        print("エラー: 無効な日付形式です。YYMMDD 形式で指定してください")
        print("例: --auto 250701")
        return False
    
    if not validate_keyword_type(args.keyword_type):
        return False
    
    if args.verbose:
        print(f"自動実行を開始します: 日付={args.auto}, キーワードタイプ={args.keyword_type}")
    
    # 自動実行モードでHTML作成を実行
    create_twitter_html_auto_main(
        date_str=args.auto,
        search_keyword=None,
        use_date=True,
        keyword_type=args.keyword_type
    )
    return True


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
        elif args.auto is not None:
            success = run_auto_command(args)
        else:
            print("エラー: 無効なコマンドです")
            print("使用可能なコマンド: --html, --merge, --extract, --auto")
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
