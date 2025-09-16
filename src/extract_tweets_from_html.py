from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone, timedelta
import re
import argparse
import sys
import os
import pyperclip

# 設定ファイルをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

def extract_tweets_from_html(html_file_path):
    """HTMLファイルからツイートデータを抽出"""

    # HTMLファイルを読み込み
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # BeautifulSoupでパース
    soup = BeautifulSoup(html_content, 'html.parser')

    tweets = []

    # ツイート要素を探す（初期の4つのみ）
    tweet_selectors = [
        'article[data-testid="tweet"]',
        'div[data-testid="tweet"]',
        'article',
        'div[role="article"]'
    ]

    for selector in tweet_selectors:
        tweet_elements = soup.select(selector)
        if tweet_elements:
            print(f"セレクタ '{selector}' で {len(tweet_elements)} 件のツイート要素を発見")
            break

    if not tweet_elements:
        print("ツイート要素が見つかりませんでした。HTMLの構造を確認します...")
        # HTMLの構造を出力
        print("HTMLの最初の1000文字:")
        print(html_content[:1000])
        return []

    for i, tweet_element in enumerate(tweet_elements):
        tweet_data = {
            'id': i + 1,
            'text': '',
            'datetime': '',
            'quote_url': '',
            'user_name': '',
            'raw_html': str(tweet_element)[:500]  # デバッグ用
        }

        try:
            # ユーザー名（表示名）を抽出
            user_name_elem = tweet_element.select_one('[data-testid="User-Name"] span')
            if user_name_elem:
                tweet_data['user_name'] = user_name_elem.get_text().strip()

            # ツイートテキストを抽出
            text_elements = tweet_element.select('[data-testid="tweetText"]')
            if text_elements:
                # テキストを取得し、改行と余分なスペースを整理
                text = text_elements[0].get_text()
                # <a href="https://..."> のリンクも抽出してテキスト末尾に追加
                link_tags = text_elements[0].select('a[href^="http"]')
                links = [a.get('href') for a in link_tags if a.get('href')]
                # ツイート要素全体からt.coリンクも抽出
                tco_links = [a.get('href') for a in tweet_element.select('a[href^="https://t.co/"]') if a.get('href')]
                # すでに本文に含まれていないリンクのみ追加
                all_links = []
                for l in links + tco_links:
                    if l and l not in text and l not in all_links:
                        all_links.append(l)
                if all_links:
                    text = text.strip() + ' ' + ' '.join(all_links)
                # 改行を削除し、複数のスペースを1つに
                text = re.sub(r'\s+', ' ', text).strip()
                tweet_data['text'] = text
            else:
                # 代替方法：テキストを含む要素を探す
                text_spans = tweet_element.select('span[dir="auto"]')
                for span in text_spans:
                    text = span.get_text()
                    text = re.sub(r'\s+', ' ', text).strip()
                    if len(text) > 10 and not text.startswith('@') and not text.startswith('#'):
                        tweet_data['text'] = text
                        break

            # 日時を抽出
            time_elements = tweet_element.select('time')
            if time_elements:
                datetime_attr = time_elements[0].get('datetime')
                if datetime_attr:
                    # ISO形式の日時をJSTに変換
                    try:
                        # UTC時間としてパース
                        dt = datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        # JSTに変換（UTC+9）
                        jst = timezone(timedelta(hours=9))
                        dt_jst = dt.astimezone(jst)
                        tweet_data['datetime'] = dt_jst.strftime('%Y/%m/%d %H:%M:%S')
                    except:
                        tweet_data['datetime'] = datetime_attr

            # ツイートURLを抽出（完全なURLに変換）
            link_elements = tweet_element.select('a[href*="/status/"]')
            for link in link_elements:
                href = link.get('href')
                if href and '/status/' in href:
                    # 相対URLを完全なURLに変換
                    if href.startswith('/'):
                        tweet_data['quote_url'] = f"https://x.com{href}"
                    elif href.startswith('http'):
                        tweet_data['quote_url'] = href
                    else:
                        tweet_data['quote_url'] = f"https://x.com/{href}"
                    break

            # 有効なツイートのみ追加（テキストが存在する場合）
            if tweet_data['text']:
                tweets.append(tweet_data)
                print(f"ツイート {i+1}: {tweet_data['text'][:50]}... ユーザー: {tweet_data['user_name']}")

        except Exception as e:
            print(f"ツイート {i+1} の抽出でエラー: {e}")
            continue

    return tweets

def format_tweet_text(text):
    """ツイートテキストをフォーマット（箇条書き対応）"""
    # 箇条書き（・）を検出して改行を追加
    lines = text.split(' ')
    formatted_lines = []

    for line in lines:
        if line.startswith('・'):
            # 箇条書きの場合は改行を追加
            formatted_lines.append('\n' + line)
        else:
            formatted_lines.append(line)

    return ' '.join(formatted_lines)

def save_tweets_to_files(tweets, base_filename="extracted_tweets", keyword_type=None):
    """ツイートデータをファイルに保存"""
    
    # 出力先ディレクトリの設定
    if keyword_type in config.KEYWORD_PREFIX_MAPPING:
        prefix = config.KEYWORD_PREFIX_MAPPING[keyword_type]
        if prefix:
            # キーワードタイプに応じた出力フォルダを取得
            folders = config.get_prefix_folders(prefix)
            txt_output_folder = folders['txt']
            json_output_folder = folders['json']
            
            # 出力フォルダが存在しなければ作成
            os.makedirs(txt_output_folder, exist_ok=True)
            os.makedirs(json_output_folder, exist_ok=True)
            
            # 出力パスを設定
            txt_path = os.path.join(txt_output_folder, f"{base_filename}.txt")
            json_path = os.path.join(json_output_folder, f"{base_filename}.json")
        else:
            # デフォルトの出力フォルダを使用
            folders = config.get_prefix_folders(None)  # デフォルトのフォルダを取得
            txt_path = os.path.join(folders['txt'], f"{base_filename}.txt")
            json_path = os.path.join(folders['json'], f"{base_filename}.json")
    else:
        # デフォルトの出力フォルダを使用
        folders = config.get_prefix_folders(None)  # デフォルトのフォルダを取得
        txt_path = os.path.join(folders['txt'], f"{base_filename}.txt")
        json_path = os.path.join(folders['json'], f"{base_filename}.json")
    
    # テキストファイルに保存
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"抽出日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"抽出ツイート数: {len(tweets)}\n")
        f.write("=" * 50 + "\n")

        for tweet in tweets:
            f.write(f"{tweet['id']}.\n")
            if tweet['user_name']:
                f.write(f"ユーザー名: {tweet['user_name']}\n")
            if tweet['datetime']:
                f.write(f"日時: {tweet['datetime']}\n")
            if tweet['quote_url']:
                f.write(f"ツイートURL: {tweet['quote_url']}\n")
            # 箇条書きをフォーマット
            formatted_text = format_tweet_text(tweet['text'])
            f.write(f"{formatted_text}\n")
            f.write("-" * 30 + "\n")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            'extraction_time': datetime.now().isoformat(),
            'tweet_count': len(tweets),
            'tweets': tweets
        }, f, ensure_ascii=False, indent=2)

    print(f"結果を {txt_path} と {json_path} に保存しました。")

def main():
    """メイン処理"""
    # コマンドライン引数の解析
    parser = argparse.ArgumentParser(description='HTMLファイルからツイートを抽出します')
    parser.add_argument('date', nargs='?', help='日付（例: 0706, 0624）')
    parser.add_argument('--keyword-type', '-k', help='キーワードタイプ (default, thai, en, chikirin, custom, manekineko)', default='default')
    parser.add_argument('--no-date', action='store_true', help='最新のHTMLファイルを使用する（日付指定なし）')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細な出力を有効化')

    args = parser.parse_args()

    # HTMLファイルの場所を検索
    html_file = None
    prefix = None

    # 指定されたkeyword_typeに基づいてファイルを検索
    if args.keyword_type in config.KEYWORD_PREFIX_MAPPING:
        prefix = config.KEYWORD_PREFIX_MAPPING[args.keyword_type]
        if prefix is not None:
            # prefixが指定されている場合はそのフォルダを検索
            folders = config.get_prefix_folders(prefix)
            html_file = os.path.join(folders['input'], f"{args.date}.html")
        else:
            # prefixがNoneの場合は通常のフォルダを検索
            html_file = os.path.join(config.INPUT_FOLDER, f"{args.date}.html")
    
    # 日付が指定されていて、かつファイルが存在しない場合にのみ検索を実行
    if args.date and not args.no_date:
        # 指定された場所にファイルがない場合は自動検索
        if html_file is None or not os.path.exists(html_file):
            # まずprefix別フォルダで検索（優先）
            for keyword_type, p in config.KEYWORD_PREFIX_MAPPING.items():
                if p is not None:
                    folders = config.get_prefix_folders(p)
                    test_html_file = os.path.join(folders['input'], f"{args.date}.html")
                    if os.path.exists(test_html_file):
                        html_file = test_html_file
                        prefix = p  # prefixを設定
                        break

            # それでも見つからない場合は通常のフォルダを検索
            if html_file is None or not os.path.exists(html_file):
                html_file = os.path.join(config.INPUT_FOLDER, f"{args.date}.html")
                prefix = None  # 通常フォルダの場合はprefixなし
    
    # --no-date が指定されている場合は最新のHTMLファイルを使用
    if args.no_date:
        # キーワードタイプに応じた入力フォルダを取得
        if prefix is not None:
            folders = config.get_prefix_folders(prefix)
            input_dir = folders['input']
        else:
            input_dir = config.INPUT_FOLDER
        
        # 最新のHTMLファイルを検索
        html_files = [f for f in os.listdir(input_dir) if f.endswith('.html')]
        if html_files:
            # 更新日時でソートして最新のファイルを取得
            html_files.sort(key=lambda x: os.path.getmtime(os.path.join(input_dir, x)), reverse=True)
            html_file = os.path.join(input_dir, html_files[0])
            print(f"最新のHTMLファイルを使用: {html_file}")

    # ファイルが存在しない場合はエラー
    if not html_file or not os.path.exists(html_file):
        print(f"エラー: 有効なHTMLファイルが見つかりません。")
        print("以下の場所を確認してください:")
        for keyword_type, p in config.KEYWORD_PREFIX_MAPPING.items():
            if p is not None:
                folders = config.get_prefix_folders(p)
                print(f"  - {folders['input']}/")
        print(f"  - {config.INPUT_FOLDER}/")
        sys.exit(1)

    # 出力ファイル名のベースを設定
    if args.no_date and not args.date:
        # 最新のファイルを使用する場合、ファイル名から日付を抽出
        base_filename = os.path.splitext(os.path.basename(html_file))[0]
        # ファイル名から日付部分を抽出 (例: 250706.html から 250706 を抽出)
        date_match = re.search(r'(\d{6})(?:\.html)?$', base_filename)
        if date_match:
            output_filename = date_match.group(1)
            if args.verbose:
                print(f"ファイル名から日付を抽出: {output_filename}")
        else:
            # 日付が見つからない場合は現在日時を使用
            output_filename = datetime.now().strftime('%y%m%d')
            if args.verbose:
                print(f"日付を検出できなかったため、現在日時を使用: {output_filename}")
    else:
        # 通常の日付指定の場合
        output_filename = args.date

    # 出力フォルダの作成
    if prefix:
        folders = config.get_prefix_folders(prefix)
    else:
        folders = config.get_prefix_folders(None)  # デフォルトのフォルダを取得
    
    txt_output_folder = folders['txt']
    json_output_folder = folders['json']

    if not os.path.exists(txt_output_folder):
        os.makedirs(txt_output_folder)
        print(f"出力フォルダ '{txt_output_folder}' を作成しました。")

    if not os.path.exists(json_output_folder):
        os.makedirs(json_output_folder)
        print(f"出力フォルダ '{json_output_folder}' を作成しました。")

    print(f"{html_file} からツイートを抽出しています...")

    # ツイートを抽出
    tweets = extract_tweets_from_html(html_file)

    if tweets:
        print(f"\n抽出完了: {len(tweets)} 件のツイートを抽出しました")

        # ツイートを抽出して保存
        save_tweets_to_files(tweets, output_filename, args.keyword_type)

        # 結果を表示
        print("\n抽出されたツイート:")
        print("=" * 50)
        for tweet in tweets:
            print(f"{tweet['id']}.")
            if tweet['user_name']:
                print(f"ユーザー名: {tweet['user_name']}")
            if tweet['datetime']:
                print(f"日時: {tweet['datetime']}")
            if tweet['quote_url']:
                print(f"ツイートURL: {tweet['quote_url']}")
            formatted_text = format_tweet_text(tweet['text'])
            print(f"{formatted_text}")
            print("-" * 30)
        # 最後のツイートの日時をuntil形式で表示
        last_dt = tweets[-1].get('datetime')
        if last_dt:
            until_str = last_dt.replace('/', '-').replace(' ', '_')
            print(f"\nuntil:{until_str}_JST")
            # クリップボードにコピー
            try:
                pyperclip.copy(f"until:{until_str}_JST")
                print(f"until日付をクリップボードにコピーしました: until:{until_str}_JST")
            except Exception as e:
                print(f"クリップボードへのコピーに失敗しました: {e}")
        return True  # 成功
    else:
        print("ツイートを抽出できませんでした。")
        return False  # 失敗

if __name__ == "__main__":
    main()
