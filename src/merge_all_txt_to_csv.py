import csv
import re
import os
import glob
from datetime import datetime

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

def merge_all_txt_to_csv():
    """全てのtxtファイルをマージしてCSVファイルを作成"""

    output_folder = "data/output"
    csv_file = os.path.join(output_folder, "csv", "all_tweets.csv")

    # txtフォルダ内の全てのtxtファイルを取得
    txt_folder = os.path.join(output_folder, "txt")
    txt_files = glob.glob(os.path.join(txt_folder, "*.txt"))

    if not txt_files:
        print("txtフォルダにtxtファイルが見つかりません。")
        return

    # csvフォルダの作成
    csv_folder = os.path.join(output_folder, "csv")
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)

    all_tweets = []

    # 各txtファイルを処理
    for txt_file in txt_files:
        print(f"処理中: {os.path.basename(txt_file)}")
        tweets = parse_txt_to_tweets(txt_file)
        all_tweets.extend(tweets)

    # 日時の昇順でソート
    all_tweets.sort(key=lambda x: x.get('timestamp', datetime.min))

    # CSVファイルに書き込み
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
    print(f"処理したファイル数: {len(txt_files)}")

if __name__ == "__main__":
    merge_all_txt_to_csv()
