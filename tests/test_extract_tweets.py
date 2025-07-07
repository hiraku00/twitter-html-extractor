#!/usr/bin/env python3
"""
Twitter HTML Extractor - Test Suite
"""

import unittest
import os
import sys
import tempfile
import shutil
from datetime import datetime

# srcフォルダをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from extract_tweets_from_html import (
    extract_tweets_from_html,
    format_tweet_text
)

class TestTweetExtraction(unittest.TestCase):
    """ツイート抽出機能のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.test_html = """
        <html>
        <body>
            <article data-testid="tweet">
                <div>
                    <time datetime="2025-06-15T03:44:35.000Z">2025年6月15日</time>
                    <div data-testid="tweetText">
                        <span>テストツイート1</span>
                    </div>
                </div>
            </article>
            <article data-testid="tweet">
                <div>
                    <time datetime="2025-06-15T04:30:00.000Z">2025年6月15日</time>
                    <div data-testid="tweetText">
                        <span>テストツイート2</span>
                    </div>
                </div>
            </article>
        </body>
        </html>
        """

        # 一時ファイルを作成
        self.temp_dir = tempfile.mkdtemp()
        self.test_html_file = os.path.join(self.temp_dir, "test.html")

        with open(self.test_html_file, 'w', encoding='utf-8') as f:
            f.write(self.test_html)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_extract_tweets_from_html(self):
        """HTMLからのツイート抽出テスト"""
        tweets = extract_tweets_from_html(self.test_html_file)

        self.assertIsInstance(tweets, list)
        self.assertEqual(len(tweets), 2)

        # 最初のツイートのテスト
        first_tweet = tweets[0]
        self.assertIn('id', first_tweet)
        self.assertIn('text', first_tweet)
        self.assertIn('datetime', first_tweet)
        self.assertEqual(first_tweet['text'], 'テストツイート1')

    def test_format_tweet_text(self):
        """ツイートテキストのフォーマットテスト"""
        test_text = "• 箇条書き1 • 箇条書き2 • 箇条書き3"
        formatted = format_tweet_text(test_text)

        self.assertIn('• 箇条書き1', formatted)
        self.assertIn('• 箇条書き2', formatted)
        self.assertIn('• 箇条書き3', formatted)

    def test_empty_html(self):
        """空のHTMLファイルのテスト"""
        empty_html = "<html><body></body></html>"
        empty_file = os.path.join(self.temp_dir, "empty.html")

        with open(empty_file, 'w', encoding='utf-8') as f:
            f.write(empty_html)

        tweets = extract_tweets_from_html(empty_file)
        self.assertEqual(len(tweets), 0)

class TestFileOperations(unittest.TestCase):
    """ファイル操作のテストクラス"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        shutil.rmtree(self.temp_dir)

    def test_nonexistent_file(self):
        """存在しないファイルのテスト"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.html")

        with self.assertRaises(FileNotFoundError):
            extract_tweets_from_html(nonexistent_file)

if __name__ == '__main__':
    unittest.main()
