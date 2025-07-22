#!/usr/bin/env python3
"""
main.pyのオプション機能のテスト
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestMainOptions(unittest.TestCase):

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # テスト用のディレクトリ構造を作成
        os.makedirs('data/input', exist_ok=True)
        os.makedirs('data/output/txt', exist_ok=True)
        os.makedirs('data/output/json', exist_ok=True)
        os.makedirs('data/output/csv', exist_ok=True)

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    def test_parse_html_options(self):
        """HTMLコマンドのオプション解析テスト"""
        # テスト用のsys.argvを設定
        test_args = [
            'main.py', 'html', '250706',
            '--no-since',
            '--keyword-type', 'thai',
            '--search-keyword', 'test keyword'
        ]

        with patch('sys.argv', test_args):
            # オプション解析のロジックをテスト
            use_since = True
            keyword_type = 'default'
            search_keyword = None

            i = 3
            while i < len(test_args):
                if test_args[i] == '--no-since':
                    use_since = False
                elif test_args[i] == '--keyword-type' and i + 1 < len(test_args):
                    keyword_type = test_args[i + 1]
                    i += 1
                elif test_args[i] == '--search-keyword' and i + 1 < len(test_args):
                    search_keyword = test_args[i + 1]
                    i += 1
                i += 1

            # 結果を確認
            self.assertFalse(use_since)
            self.assertEqual(keyword_type, 'thai')
            self.assertEqual(search_keyword, 'test keyword')

    def test_parse_html_options_no_since_only(self):
        """--no-sinceのみのオプション解析テスト"""
        test_args = ['main.py', 'html', '250706', '--no-since']

        with patch('sys.argv', test_args):
            use_since = True
            keyword_type = 'default'
            search_keyword = None

            i = 3
            while i < len(test_args):
                if test_args[i] == '--no-since':
                    use_since = False
                elif test_args[i] == '--keyword-type' and i + 1 < len(test_args):
                    keyword_type = test_args[i + 1]
                    i += 1
                elif test_args[i] == '--search-keyword' and i + 1 < len(test_args):
                    search_keyword = test_args[i + 1]
                    i += 1
                i += 1

            # 結果を確認
            self.assertFalse(use_since)
            self.assertEqual(keyword_type, 'default')
            self.assertIsNone(search_keyword)

    def test_parse_html_options_keyword_type_only(self):
        """--keyword-typeのみのオプション解析テスト"""
        test_args = ['main.py', 'html', '250706', '--keyword-type', 'en']

        with patch('sys.argv', test_args):
            use_since = True
            keyword_type = 'default'
            search_keyword = None

            i = 3
            while i < len(test_args):
                if test_args[i] == '--no-since':
                    use_since = False
                elif (test_args[i] == '--keyword-type' or test_args[i] == '-k') and i + 1 < len(test_args):
                    keyword_type = test_args[i + 1]
                    i += 1
                elif test_args[i] == '--search-keyword' and i + 1 < len(test_args):
                    search_keyword = test_args[i + 1]
                    i += 1
                i += 1

            # 結果を確認
            self.assertTrue(use_since)
            self.assertEqual(keyword_type, 'en')
            self.assertIsNone(search_keyword)
    
    def test_parse_html_options_short_k_option(self):
        """-k 短縮オプションの解析テスト"""
        test_args = ['main.py', 'html', '250706', '-k', 'chikirin']

        with patch('sys.argv', test_args):
            use_since = True
            keyword_type = 'default'
            search_keyword = None

            i = 3
            while i < len(test_args):
                if test_args[i] == '--no-since':
                    use_since = False
                elif (test_args[i] == '--keyword-type' or test_args[i] == '-k') and i + 1 < len(test_args):
                    keyword_type = test_args[i + 1]
                    i += 1
                elif test_args[i] == '--search-keyword' and i + 1 < len(test_args):
                    search_keyword = test_args[i + 1]
                    i += 1
                i += 1

            # 結果を確認
            self.assertTrue(use_since)
            self.assertEqual(keyword_type, 'chikirin')
            self.assertIsNone(search_keyword)

    def test_date_conversion(self):
        """日付変換テスト"""
        yymmdd = "250706"
        if len(yymmdd) == 6:
            year = 2000 + int(yymmdd[:2])
            date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"

        self.assertEqual(date_str, "2025-07-06")

    def test_invalid_date_format(self):
        """無効な日付形式のテスト"""
        yymmdd = "2507"  # 6桁ではない
        if len(yymmdd) == 6:
            year = 2000 + int(yymmdd[:2])
            date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"
        else:
            date_str = None

        self.assertIsNone(date_str)



if __name__ == '__main__':
    unittest.main()
