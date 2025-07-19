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

def save_tweets_to_files(tweets, base_filename="extracted_tweets"):
    """ツイートデータをファイルに保存"""

    # テキストファイルに保存（txtフォルダ）
    txt_path = f"{base_filename}.txt"
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

    # JSONファイルに保存（jsonフォルダ）
    json_folder = os.path.join(os.path.dirname(os.path.dirname(base_filename)), "json")
    if not os.path.exists(json_folder):
        os.makedirs(json_folder)

    json_filename = os.path.basename(base_filename) + ".json"
    json_path = os.path.join(json_folder, json_filename)

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
    parser.add_argument('date', help='日付（例: 250706, 250624）')

    args = parser.parse_args()

    # HTMLファイルの場所を自動検出
    html_file = None
    prefix = None

    # まず通常のフォルダで検索
    input_folder = config.INPUT_FOLDER
    html_file = os.path.join(input_folder, f"{args.date}.html")

    if not os.path.exists(html_file):
        # 通常のフォルダにない場合、prefix別フォルダを検索
        for keyword_type, prefix in config.KEYWORD_PREFIX_MAPPING.items():
            if prefix is not None:
                folders = config.get_prefix_folders(prefix)
                test_html_file = os.path.join(folders['input'], f"{args.date}.html")
                if os.path.exists(test_html_file):
                    html_file = test_html_file
                    break

    if html_file is None or not os.path.exists(html_file):
        print(f"エラー: ファイル '{args.date}.html' が見つかりません。")
        print("以下の場所を確認してください:")
        print(f"  - {config.INPUT_FOLDER}/")
        for keyword_type, prefix in config.KEYWORD_PREFIX_MAPPING.items():
            if prefix is not None:
                folders = config.get_prefix_folders(prefix)
                print(f"  - {folders['input']}/")
        sys.exit(1)

    # prefixを決定
    if html_file.startswith(config.INPUT_FOLDER):
        prefix = None
    else:
        for keyword_type, p in config.KEYWORD_PREFIX_MAPPING.items():
            if p is not None:
                folders = config.get_prefix_folders(p)
                if html_file.startswith(folders['input']):
                    prefix = p
                    break

    # 出力フォルダの設定
    folders = config.get_prefix_folders(prefix)
    output_filename = os.path.join(folders['txt'], args.date)

    # 出力フォルダの作成
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

        # ファイルに保存
        save_tweets_to_files(tweets, output_filename)

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
    else:
        print("ツイートを抽出できませんでした。")

if __name__ == "__main__":
    main()
