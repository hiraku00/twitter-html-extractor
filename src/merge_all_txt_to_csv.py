import csv
import re
import os
import glob
import sys
from datetime import datetime

# 設定ファイルをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import config

def parse_txt_to_tweets(txt_file_path):
    """txtファイルを解析してツイートデータを抽出"""

    tweets = []
    current_tweet = {}

    with open(txt_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # ユーザー名の行を検出
        if line.startswith('ユーザー名: '):
            user_name = line.replace('ユーザー名: ', '')
            current_tweet['user_name'] = user_name

        # 日時の行を検出
        elif line.startswith('日時: '):
            datetime_str = line.replace('日時: ', '')
            current_tweet['datetime'] = datetime_str
            # 日時をパースしてソート用のタイムスタンプを作成
            try:
                dt = datetime.strptime(datetime_str, '%Y/%m/%d %H:%M:%S')
                current_tweet['timestamp'] = dt
            except:
                current_tweet['timestamp'] = datetime.min

        # URLの行を検出
        elif line.startswith('ツイートURL: '):
            url = line.replace('ツイートURL: ', '')
            current_tweet['url'] = url

        # ツイート内容の行を検出（日時、URL、区切り線以外の行）
        elif (line and
              not line.startswith('抽出日時:') and
              not line.startswith('抽出ツイート数:') and
              not line.startswith('=') and
              not line.startswith('-') and
              not line.startswith('ツイートURL:') and
              not line.endswith('.') and  # ID行を除外
              not re.match(r'^\d+\.$', line)):  # 数字.の行を除外

            # ツイート内容を結合
            if 'text' in current_tweet:
                current_tweet['text'] += ' ' + line
            else:
                current_tweet['text'] = line

        # 区切り線でツイートの終了を検出
        elif line.startswith('-' * 30):
            if current_tweet and 'text' in current_tweet:
                # ファイル名を追加
                current_tweet['source_file'] = os.path.basename(txt_file_path)
                tweets.append(current_tweet.copy())
            current_tweet = {}

    # 最後のツイートも追加
    if current_tweet and 'text' in current_tweet:
        current_tweet['source_file'] = os.path.basename(txt_file_path)
        tweets.append(current_tweet)

    return tweets

def merge_all_txt_to_csv(keyword_type='default'):
    """指定されたキーワードタイプのtxtファイルをマージしてCSVファイルを作成"""

    all_tweets = []
    processed_files = []

    # キーワードタイプの検証
    if keyword_type not in config.KEYWORD_PREFIX_MAPPING:
        print(f"エラー: 無効なキーワードタイプ '{keyword_type}'")
        print(f"使用可能なキーワードタイプ: {', '.join(config.KEYWORD_PREFIX_MAPPING.keys())}")
        return

    # 指定されたキーワードタイプのフォルダからtxtファイルを取得
    prefix = config.KEYWORD_PREFIX_MAPPING.get(keyword_type)
    folders = config.get_prefix_folders(prefix)
    txt_folder = folders['txt']
    txt_files = glob.glob(os.path.join(txt_folder, "*.txt"))

    if txt_files:
        print(f"{keyword_type}フォルダから {len(txt_files)} ファイルを処理:")
        for txt_file in txt_files:
            print(f"  処理中: {os.path.basename(txt_file)}")
            tweets = parse_txt_to_tweets(txt_file)
            all_tweets.extend(tweets)
            processed_files.append(txt_file)
    else:
        print(f"{keyword_type}フォルダにtxtファイルが見つかりません。")
        print(f"確認してください: {txt_folder}/")
        return

    if not processed_files:
        print("txtファイルが見つかりません。")
        return

    # 日時の昇順でソート
    all_tweets.sort(key=lambda x: x.get('timestamp', datetime.min))

    # CSVファイル名を決定
    if keyword_type == 'default':
        csv_filename = "all_tweets.csv"
    else:
        csv_filename = f"{keyword_type}_tweets.csv"

    # CSVファイルに書き込み
    csv_folder = folders['csv']
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    csv_file = os.path.join(csv_folder, csv_filename)

    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ユーザー名', '日時', 'URL', 'ツイート内容', '元ファイル'])

        for tweet in all_tweets:
            writer.writerow([
                tweet.get('user_name', ''),
                tweet.get('datetime', ''),
                tweet.get('url', ''),
                tweet.get('text', ''),
                tweet.get('source_file', '')
            ])

    print(f"マージ完了: {csv_file}")
    print(f"総ツイート数: {len(all_tweets)}")
    print(f"処理したファイル数: {len(processed_files)}")

if __name__ == "__main__":
    merge_all_txt_to_csv()
