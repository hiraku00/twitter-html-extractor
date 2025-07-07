from bs4 import BeautifulSoup
import json
from datetime import datetime, timezone, timedelta
import re
import argparse
import sys
import os

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
            'raw_html': str(tweet_element)[:500]  # デバッグ用
        }

        try:
            # ツイートテキストを抽出
            text_elements = tweet_element.select('[data-testid="tweetText"]')
            if text_elements:
                # テキストを取得し、改行と余分なスペースを整理
                text = text_elements[0].get_text()
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
                print(f"ツイート {i+1}: {tweet_data['text'][:50]}...")

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

    # 入力・出力フォルダの設定
    input_folder = "data/input"
    output_folder = "data/output"

    # HTMLファイル名を生成
    html_file = os.path.join(input_folder, f"{args.date}.html")
    output_filename = os.path.join(output_folder, "txt", args.date)

    # 入力フォルダの存在確認
    if not os.path.exists(input_folder):
        print(f"エラー: 入力フォルダ '{input_folder}' が存在しません。")
        sys.exit(1)

    # 出力フォルダの作成
    txt_output_folder = os.path.join(output_folder, "txt")
    json_output_folder = os.path.join(output_folder, "json")

    if not os.path.exists(txt_output_folder):
        os.makedirs(txt_output_folder)
        print(f"出力フォルダ '{txt_output_folder}' を作成しました。")

    if not os.path.exists(json_output_folder):
        os.makedirs(json_output_folder)
        print(f"出力フォルダ '{json_output_folder}' を作成しました。")

    # HTMLファイルの存在確認
    if not os.path.exists(html_file):
        print(f"エラー: ファイル '{html_file}' が存在しません。")
        sys.exit(1)

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
            if tweet['datetime']:
                print(f"日時: {tweet['datetime']}")
            if tweet['quote_url']:
                print(f"ツイートURL: {tweet['quote_url']}")
            formatted_text = format_tweet_text(tweet['text'])
            print(f"{formatted_text}")
            print("-" * 30)
    else:
        print("ツイートを抽出できませんでした。")

if __name__ == "__main__":
    main()
