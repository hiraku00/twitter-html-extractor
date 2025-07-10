#!/usr/bin/env python3
"""
Twitter自動化スクリプトのテスト
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# srcフォルダをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from create_twitter_html_auto import save_html_to_file, get_position

class TestCreateTwitterHtmlAuto(unittest.TestCase):

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # テスト用のディレクトリ構造を作成
        os.makedirs('data/input', exist_ok=True)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_save_html_to_file(self):
        """HTMLファイル保存機能のテスト"""
        html_content = "<html><body><h1>Test HTML</h1></body></html>"
        date_str = "2025-01-15"

        # ファイル保存を実行
        filepath = save_html_to_file(html_content, date_str)

        # ファイルが作成されたことを確認
        self.assertTrue(os.path.exists(filepath))

        # ファイル内容を確認
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_content = f.read()

        self.assertEqual(saved_content, html_content)

        # ファイル名が正しいことを確認
        expected_filename = f"twitter_{date_str}.html"
        self.assertIn(expected_filename, filepath)

    @patch('builtins.input')
    @patch('pyautogui.position')
    def test_get_position(self, mock_position, mock_input):
        """位置取得機能のテスト"""
        # モックの設定
        mock_position.return_value = (100, 200)
        mock_input.side_effect = ['', 'yes']  # Enterキーとyes

        # 位置取得を実行
        position = get_position("テスト用プロンプト")

        # 結果を確認
        self.assertEqual(position, (100, 200))
        mock_position.assert_called_once()

    @patch('builtins.input')
    @patch('pyautogui.position')
    def test_get_position_retry(self, mock_position, mock_input):
        """位置取得の再試行テスト"""
        # モックの設定
        mock_position.side_effect = [(100, 200), (150, 250)]
        mock_input.side_effect = ['', 'no', '', 'yes']  # Enterキー、no、Enterキー、yes

        # 位置取得を実行
        position = get_position("テスト用プロンプト")

        # 結果を確認
        self.assertEqual(position, (150, 250))
        self.assertEqual(mock_position.call_count, 2)

if __name__ == '__main__':
    unittest.main()
