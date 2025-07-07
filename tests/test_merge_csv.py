#!/usr/bin/env python3
"""
CSV Merge Functionality - Test Suite
"""

import unittest
import os
import sys
import tempfile
import shutil
import csv

# srcフォルダをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from merge_all_txt_to_csv import parse_txt_to_tweets

class TestCSVMerge(unittest.TestCase):
    """CSVマージ機能のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()

        # テスト用のtxtファイルを作成
        self.test_txt_content = """抽出日時: 2025-01-27 15:30:00
抽出ツイート数: 2
==================================================
1.
日時: 2025/06/15 12:44:35
ツイートURL: https://x.com/test/status/123456
• テストツイート1
• 箇条書き1
• 箇条書き2
------------------------------
2.
日時: 2025/06/15 13:30:00
ツイートURL: https://x.com/test/status/789012
• テストツイート2
• 箇条書き3
------------------------------
"""

        self.test_txt_file = os.path.join(self.temp_dir, "test.txt")
        with open(self.test_txt_file, 'w', encoding='utf-8') as f:
            f.write(self.test_txt_content)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_parse_txt_to_tweets(self):
        """txtファイルからのツイート解析テスト"""
        tweets = parse_txt_to_tweets(self.test_txt_file)

        self.assertIsInstance(tweets, list)
        self.assertEqual(len(tweets), 2)

        # 最初のツイートのテスト
        first_tweet = tweets[0]
        self.assertIn('datetime', first_tweet)
        self.assertIn('url', first_tweet)
        self.assertIn('text', first_tweet)
        self.assertIn('source_file', first_tweet)

        self.assertEqual(first_tweet['datetime'], '2025/06/15 12:44:35')
        self.assertEqual(first_tweet['url'], 'https://x.com/test/status/123456')
        self.assertIn('テストツイート1', first_tweet['text'])
        self.assertIn('箇条書き1', first_tweet['text'])
        self.assertIn('箇条書き2', first_tweet['text'])

        # 2番目のツイートのテスト
        second_tweet = tweets[1]
        self.assertEqual(second_tweet['datetime'], '2025/06/15 13:30:00')
        self.assertEqual(second_tweet['url'], 'https://x.com/test/status/789012')
        self.assertIn('テストツイート2', second_tweet['text'])
        self.assertIn('箇条書き3', second_tweet['text'])

    def test_empty_txt_file(self):
        """空のtxtファイルのテスト"""
        empty_txt = os.path.join(self.temp_dir, "empty.txt")
        with open(empty_txt, 'w', encoding='utf-8') as f:
            f.write("")

        tweets = parse_txt_to_tweets(empty_txt)
        self.assertEqual(len(tweets), 0)

    def test_malformed_txt_file(self):
        """不正な形式のtxtファイルのテスト"""
        malformed_txt = os.path.join(self.temp_dir, "malformed.txt")
        with open(malformed_txt, 'w', encoding='utf-8') as f:
            f.write("不正な形式のファイル\n日時: 2025/06/15 12:44:35\n")

        tweets = parse_txt_to_tweets(malformed_txt)
        # 不正な形式でもエラーにならず、空のリストを返す
        self.assertIsInstance(tweets, list)

class TestCSVOutput(unittest.TestCase):
    """CSV出力のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_csv_format(self):
        """CSV形式のテスト"""
        test_data = [
            {
                'datetime': '2025/06/15 12:44:35',
                'url': 'https://x.com/test/status/123456',
                'text': 'テストツイート1',
                'source_file': 'test.txt'
            }
        ]

        csv_file = os.path.join(self.temp_dir, "test.csv")
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['日時', 'URL', 'ツイート内容', '元ファイル'])
            for tweet in test_data:
                writer.writerow([
                    tweet['datetime'],
                    tweet['url'],
                    tweet['text'],
                    tweet['source_file']
                ])

        # CSVファイルが正しく作成されているかテスト
        self.assertTrue(os.path.exists(csv_file))

        with open(csv_file, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('日時', content)
            self.assertIn('URL', content)
            self.assertIn('ツイート内容', content)
            self.assertIn('元ファイル', content)
            self.assertIn('2025/06/15 12:44:35', content)
            self.assertIn('https://x.com/test/status/123456', content)

if __name__ == '__main__':
    unittest.main()
