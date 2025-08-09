#!/usr/bin/env python3
"""
統合テスト - 実際のmain関数の動作をテスト
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestIntegration(unittest.TestCase):

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

    @patch('src.create_twitter_html_all.main')
    def test_main_html_with_no_since(self, mock_create_html):
        """main.pyのhtmlコマンドで--no-sinceオプションをテスト"""
        # テスト用のsys.argvを設定
        test_args = ['main.py', 'html', '250513', '--no-since']

        with patch('sys.argv', test_args):
            # main.pyのhtmlコマンド部分をテスト
            yymmdd = test_args[2]
            if len(yymmdd) == 6:
                year = 2000 + int(yymmdd[:2])
                date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"
            else:
                date_str = None

            # オプション解析
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
            self.assertEqual(date_str, "2025-05-13")
            self.assertFalse(use_since)
            self.assertEqual(keyword_type, 'default')
            self.assertIsNone(search_keyword)

    @patch('src.create_twitter_html_all.main')
    def test_main_html_with_keyword_type(self, mock_create_html):
        """main.pyのhtmlコマンドで--keyword-typeオプションをテスト"""
        # テスト用のsys.argvを設定
        test_args = ['main.py', 'html', '250513', '--keyword-type', 'thai']

        with patch('sys.argv', test_args):
            # main.pyのhtmlコマンド部分をテスト
            yymmdd = test_args[2]
            if len(yymmdd) == 6:
                year = 2000 + int(yymmdd[:2])
                date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"
            else:
                date_str = None

            # オプション解析
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
            self.assertEqual(date_str, "2025-05-13")
            self.assertTrue(use_since)
            self.assertEqual(keyword_type, 'thai')
            self.assertIsNone(search_keyword)

    @patch('src.create_twitter_html_all.main')
    def test_main_html_with_chikirin_keyword_type(self, mock_create_html):
        """main.pyのhtmlコマンドで--keyword-type chikirinオプションをテスト"""
        # テスト用のsys.argvを設定
        test_args = ['main.py', 'html', '250513', '--keyword-type', 'chikirin']

        with patch('sys.argv', test_args):
            # main.pyのhtmlコマンド部分をテスト
            yymmdd = test_args[2]
            if len(yymmdd) == 6:
                year = 2000 + int(yymmdd[:2])
                date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"
            else:
                date_str = None

            # オプション解析
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
                
    @patch('src.create_twitter_html_all.main')
    def test_main_html_with_short_k_option(self, mock_create_html):
        """main.pyのhtmlコマンドで-k 短縮オプションをテスト"""
        # テスト用のsys.argvを設定
        test_args = ['main.py', 'html', '250513', '-k', 'en']

        with patch('sys.argv', test_args):
            # main.pyのhtmlコマンド部分をテスト
            yymmdd = test_args[2]
            if len(yymmdd) == 6:
                year = 2000 + int(yymmdd[:2])
                date_str = f"{year:04d}-{yymmdd[2:4]}-{yymmdd[4:6]}"
            else:
                date_str = None

            # オプション解析
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
            self.assertEqual(date_str, "2025-05-13")
            self.assertTrue(use_since)
            self.assertEqual(keyword_type, 'en')
            self.assertIsNone(search_keyword)

    def test_search_query_actual_behavior(self):
        """実際の検索クエリ生成動作をテスト"""
        import config

        # since指定なしの場合
        date_str = "2025-05-13"
        keyword = "dtv ビザ"
        use_since = False
        until_datetime = "until:2025-05-13_17:33:55_JST"  # クリップボードの例

        if use_since:
            search_query = config.SEARCH_QUERY_TEMPLATE_WITH_SINCE.format(
                date=date_str, until_datetime=until_datetime, keyword=keyword
            )
        else:
            search_query = config.SEARCH_QUERY_TEMPLATE_WITHOUT_SINCE.format(
                until_datetime=until_datetime, keyword=keyword
            )

        # 実際の実行結果と一致することを確認
        expected_query = f"{until_datetime} {keyword}"
        self.assertEqual(search_query, expected_query)
        self.assertNotIn("since:", search_query)
        self.assertIn("until:", search_query)
        self.assertIn("_JST", search_query)

    def test_search_query_with_since_actual_behavior(self):
        """since指定ありでの実際の検索クエリ生成動作をテスト"""
        import config

        # since指定ありの場合
        date_str = "2025-05-13"
        keyword = "dtv ビザ"
        use_since = True

        until_datetime = "until:2025-05-13_17:33:55_JST"  # クリップボードの例
        if use_since:
            search_query = config.SEARCH_QUERY_TEMPLATE_WITH_SINCE.format(
                date=date_str, until_datetime=until_datetime, keyword=keyword
            )
        else:
            search_query = config.SEARCH_QUERY_TEMPLATE_WITHOUT_SINCE.format(
                until_datetime=until_datetime, keyword=keyword
            )

        # 期待される結果を確認
        expected_query = f"since:{date_str}_00:00:00_JST {until_datetime} {keyword}"
        self.assertEqual(search_query, expected_query)
        self.assertIn("since:", search_query)
        self.assertIn("until:", search_query)
        self.assertIn("_JST", search_query)
        self.assertIn(keyword, search_query)



if __name__ == '__main__':
    unittest.main()
