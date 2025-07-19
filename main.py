#!/usr/bin/env python3
"""
Twitter HTML Extractor - Main Entry Point
"""

import sys
import os

# srcフォルダをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from extract_tweets_from_html import main as extract_main
from merge_all_txt_to_csv import merge_all_txt_to_csv
from create_twitter_html_auto import main as create_twitter_html_auto_main

def main():
    """メインエントリーポイント"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  ツイート抽出: python main.py extract <日付>")
        print("  マージ実行:   python main.py merge")
        print("  HTML作成:     python main.py html <日付> [オプション]")
        print("  Twitter自動化: python main.py auto <日付>")
        print("")
        print("HTML作成のオプション:")
        print("  --no-date: 日付指定なしで検索（untilは指定、日付引数不要）")
        print("  --keyword-type <type>: 検索キーワードの種類 (default, thai, en, chikirin, custom)")
        print("  --search-keyword <keyword>: カスタム検索キーワード")
        print("")
        print("例:")
        print("  python main.py extract 250706")
        print("  python main.py merge")
        print("  python main.py html 250701")
        print("  python main.py html --no-date")
        print("  python main.py html --no-date --keyword-type thai")
        print("  python main.py html 250701 --search-keyword 'ニュース ビザ'")
        print("  python main.py html 250701 --keyword-type chikirin")
        print("  python main.py auto 2025-01-15")
        sys.exit(1)

    command = sys.argv[1]

    if command == "extract":
        if len(sys.argv) < 3:
            print("エラー: 日付を指定してください")
            print("例: python main.py extract 250706")
            sys.exit(1)

        # extract_tweets_from_html.pyのmain関数を呼び出し
        # 引数を調整して渡す
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        extract_main()

    elif command == "merge":
        merge_all_txt_to_csv()

    elif command == "html":
        # オプション引数の解析
        use_date = True
        keyword_type = 'default'
        search_keyword = None

        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == '--no-date':
                use_date = False
            elif sys.argv[i] == '--keyword-type' and i + 1 < len(sys.argv):
                keyword_type = sys.argv[i + 1]
                i += 1
            elif sys.argv[i] == '--search-keyword' and i + 1 < len(sys.argv):
                search_keyword = sys.argv[i + 1]
                i += 1
            i += 1

        # 通常の場合、日付引数は必須
        if use_date:
            if len(sys.argv) < 3:
                print("エラー: 日付を指定してください")
                print("例: python main.py html 250701")
                print("日付はYYMMDD形式（例：250701）で指定してください")
                print("")
                print("オプション:")
                print("  --no-date: 日付指定なしで検索（untilは指定、日付引数不要）")
                print("  --keyword-type <type>: 検索キーワードの種類 (default, thai, en, custom)")
                print("  --search-keyword <keyword>: カスタム検索キーワード")
                sys.exit(1)
            yymmdd = sys.argv[2]
            if len(yymmdd) == 6 and yymmdd.isdigit():
                year = 2000 + int(yymmdd[:2])
                date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"
            else:
                print("エラー: 日付はYYMMDD形式で指定してください")
                print("例: 250701 (2025年7月1日)")
                sys.exit(1)
        else:
            # --no-dateの場合、ダミーの日付を設定（実際にはクリップボードから取得される）
            date_str = "2025-01-01"  # ダミー値

        from src.create_twitter_html_auto import main as twitter_html_main
        # HTML作成を実行
        result = twitter_html_main(date_str, search_keyword, use_date, keyword_type)

        # HTML作成が成功した場合、自動的にextract処理を実行
        if result:
            print("\n=== 自動extract処理を開始 ===")
            try:
                # 生成されたHTMLファイルの日付を取得
                if use_date:
                    # 通常の日付指定の場合
                    extract_date = yymmdd
                else:
                    # --no-dateの場合、HTML作成時に生成されたファイル名から日付を取得
                    # resultはファイルパスなので、ファイル名から日付を抽出
                    filename = os.path.basename(result)
                    if filename.endswith('.html'):
                        extract_date = filename[:-5]  # .htmlを除去
                    else:
                        print(f"エラー: 生成されたファイル名が不正です: {result}")
                        sys.exit(1)

                # extract処理を実行
                print(f"extract処理を実行: {extract_date}")
                # extract_main関数を呼び出すために引数を設定
                original_argv = sys.argv.copy()
                sys.argv = [sys.argv[0], extract_date]
                extract_main()
                sys.argv = original_argv
                print("自動extract処理が完了しました")

            except Exception as e:
                print(f"自動extract処理でエラーが発生しました: {e}")

    elif command == "auto":
        if len(sys.argv) < 3:
            print("エラー: 日付を指定してください")
            print("例: python main.py auto 2025-01-15")
            sys.exit(1)
        # create_twitter_html_auto.pyのmain関数を呼び出し
        # 引数を調整して渡す
        sys.argv = [sys.argv[0]] + sys.argv[2:]
        create_twitter_html_auto_main()

    else:
        print(f"エラー: 不明なコマンド '{command}'")
        print("使用可能なコマンド: extract, merge, html, auto")
        sys.exit(1)

if __name__ == "__main__":
    main()
