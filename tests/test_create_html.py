#!/usr/bin/env python3
"""
HTMLファイル作成スクリプトのテスト
"""

import unittest
import os
import tempfile
import shutil
import sys
from unittest.mock import patch, MagicMock

# テスト対象のモジュールをインポート
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from create_html_from_clipboard import create_html_from_clipboard

class TestHTMLCreation(unittest.TestCase):
    """HTMLファイル作成のテスト"""

    def setUp(self):
        """テスト前の準備"""
        # 一時ディレクトリを作成
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # data/inputディレクトリを作成
        os.makedirs('data/input', exist_ok=True)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch('create_html_from_clipboard.pyperclip.paste')
    def test_create_html_success(self, mock_paste):
        """HTMLファイル作成の成功テスト"""
        # モックの設定
        mock_paste.return_value = '<html><body><div>テストHTML</div></body></html>'

        # テスト実行
        result = create_html_from_clipboard('test250701')

        # 結果の検証
        self.assertTrue(result)

        # ファイルが作成されているか確認
        expected_file = 'data/input/test250701.html'
        self.assertTrue(os.path.exists(expected_file))

        # ファイル内容の確認
        with open(expected_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, '<html><body><div>テストHTML</div></body></html>')

    @patch('create_html_from_clipboard.pyperclip.paste')
    def test_create_html_empty_clipboard(self, mock_paste):
        """空のクリップボードのテスト"""
        # モックの設定
        mock_paste.return_value = ''

        # テスト実行
        result = create_html_from_clipboard('test250702')

        # 結果の検証
        self.assertFalse(result)

        # ファイルが作成されていないか確認
        expected_file = 'data/input/test250702.html'
        self.assertFalse(os.path.exists(expected_file))

    @patch('create_html_from_clipboard.pyperclip.paste')
    def test_create_html_whitespace_only(self, mock_paste):
        """空白文字のみのクリップボードのテスト"""
        # モックの設定
        mock_paste.return_value = '   \n\t   '

        # テスト実行
        result = create_html_from_clipboard('test250703')

        # 結果の検証
        self.assertFalse(result)

        # ファイルが作成されていないか確認
        expected_file = 'data/input/test250703.html'
        self.assertFalse(os.path.exists(expected_file))

    @patch('create_html_from_clipboard.pyperclip.paste')
    @patch('builtins.input')
    def test_create_html_file_exists_overwrite(self, mock_input, mock_paste):
        """既存ファイルの上書きテスト"""
        # 既存ファイルを作成
        existing_file = 'data/input/test250704.html'
        with open(existing_file, 'w', encoding='utf-8') as f:
            f.write('既存のHTML')

        # モックの設定
        mock_paste.return_value = '<html><body>新しいHTML</body></html>'
        mock_input.return_value = 'y'

        # テスト実行
        result = create_html_from_clipboard('test250704')

        # 結果の検証
        self.assertTrue(result)

        # ファイル内容が更新されているか確認
        with open(existing_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, '<html><body>新しいHTML</body></html>')

    @patch('create_html_from_clipboard.pyperclip.paste')
    @patch('builtins.input')
    def test_create_html_file_exists_cancel(self, mock_input, mock_paste):
        """既存ファイルのキャンセルテスト"""
        # 既存ファイルを作成
        existing_file = 'data/input/test250705.html'
        original_content = '既存のHTML'
        with open(existing_file, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # モックの設定
        mock_paste.return_value = '<html><body>新しいHTML</body></html>'
        mock_input.return_value = 'n'

        # テスト実行
        result = create_html_from_clipboard('test250705')

        # 結果の検証
        self.assertFalse(result)

        # ファイル内容が変更されていないか確認
        with open(existing_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, original_content)

    @patch('create_html_from_clipboard.pyperclip.paste')
    def test_create_html_input_folder_creation(self, mock_paste):
        """入力フォルダの自動作成テスト"""
        # data/inputディレクトリを削除
        if os.path.exists('data/input'):
            shutil.rmtree('data/input')

        # モックの設定
        mock_paste.return_value = '<html><body>テストHTML</body></html>'

        # テスト実行
        result = create_html_from_clipboard('test250706')

        # 結果の検証
        self.assertTrue(result)

        # ディレクトリが作成されているか確認
        self.assertTrue(os.path.exists('data/input'))

        # ファイルが作成されているか確認
        expected_file = 'data/input/test250706.html'
        self.assertTrue(os.path.exists(expected_file))

if __name__ == '__main__':
    unittest.main()
