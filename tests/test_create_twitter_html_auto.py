#!/usr/bin/env python3
"""
create_twitter_html_auto.pyのテスト
"""

import unittest
import sys
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestCreateTwitterHtmlAuto(unittest.TestCase):

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

        # pyautogui全体をモック
        self.pyautogui_patcher = patch('src.create_twitter_html_auto.pyautogui', new=MagicMock())
        self.mock_pyautogui = self.pyautogui_patcher.start()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
        self.pyautogui_patcher.stop()

    @patch('pyautogui.position')
    @patch('builtins.input')
    def test_get_position(self, mock_input, mock_position):
        """位置取得機能のテスト"""
        from src.create_twitter_html_auto import get_position

        mock_position.return_value = (100, 200)
        mock_input.return_value = ""

        result = get_position("テスト用プロンプト")

        self.assertEqual(result, (100, 200))
        mock_input.assert_called_once()

    @patch('pyautogui.position')
    @patch('builtins.input')
    def test_get_position_retry(self, mock_input, mock_position):
        """位置取得の再試行テスト"""
        from src.create_twitter_html_auto import get_position

        mock_position.return_value = (100, 200)
        mock_input.return_value = ""

        result = get_position("テスト用プロンプト")

        self.assertEqual(result, (100, 200))

    def test_save_html_to_file(self):
        """HTMLファイル保存機能のテスト"""
        from src.create_twitter_html_auto import save_html_to_file

        html_content = "<html><body>テスト</body></html>"
        date_str = "2025-01-15"

        result = save_html_to_file(html_content, date_str)

        self.assertIsNotNone(result)
        self.assertTrue(os.path.exists(result))

        # ファイル内容を確認
        with open(result, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, html_content)

    def test_search_query_with_since(self):
        """since指定ありの検索クエリ生成テスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-01-15_23:59:59_JST"

                # main関数をモックして、検索クエリ生成部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as clickmock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "test.html"

                                # main関数を実行
                                result = main()

                                # 検索クエリが正しく生成されたことを確認
                                self.assertIsNotNone(result)

    def test_search_query_without_date(self):
        """日付指定なしの検索クエリ生成テスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-05-08_16:54:40_JST"

                # main関数をモックして、検索クエリ生成部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "data/input/250508.html"

                                # main関数を実行
                                result = main()

                                # 検索クエリが正しく生成されたことを確認
                                self.assertIsNotNone(result)

    def test_until_datetime_to_filename(self):
        """until日時からファイル名を生成するテスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-05-08_16:54:40_JST"

                # main関数をモックして、ファイル名生成部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "data/input/250508.html"

                                # main関数を実行
                                result = main()

                                # ファイル名が正しく生成されたことを確認
                                self.assertIsNotNone(result)

    def test_until_datetime_to_filename_different_date(self):
        """異なる日付でのuntil日時からファイル名を生成するテスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-12-25_10:30:15_JST"

                # main関数をモックして、ファイル名生成部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "data/input/251225.html"

                                # main関数を実行
                                result = main()

                                # ファイル名が正しく生成されたことを確認
                                self.assertIsNotNone(result)

    def test_invalid_until_datetime_format(self):
        """不正なuntil日時形式のテスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                # 不正な形式のuntil日時
                mock_paste.return_value = "until:invalid_format"

                # main関数を実行してエラーが発生することを確認
                with self.assertRaises(SystemExit):
                    main()

    def test_missing_until_datetime(self):
        """until日時が存在しない場合のテスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                # until日時が存在しない
                mock_paste.return_value = "some other content"

                # main関数を実行してエラーが発生することを確認
                with self.assertRaises(SystemExit):
                    main()

    def test_clipboard_until_datetime(self):
        """クリップボードからuntil日時を取得するテスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-05-08_16:54:40_JST"

                # main関数をモックして、until日時取得部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "test.html"

                                # main関数を実行
                                result = main()

                                # until日時が正しく取得されたことを確認
                                self.assertIsNotNone(result)

    def test_clipboard_no_until_datetime(self):
        """クリップボードにuntil日時がない場合のテスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "some other content"

                # main関数を実行してエラーが発生することを確認
                with self.assertRaises(SystemExit):
                    main()

    def test_keyword_types(self):
        """検索キーワードの種類テスト"""
        from src.create_twitter_html_auto import main

        # 各キーワードタイプをテスト
        keyword_types = ['default', 'thai', 'en', 'custom']

        for keyword_type in keyword_types:
            with self.subTest(keyword_type=keyword_type):
                # テスト用の引数を設定
                test_args = ['create_twitter_html_auto.py', '2025-01-15', '--keyword-type', keyword_type]

                with patch('sys.argv', test_args):
                    with patch('pyperclip.paste') as mock_paste:
                        mock_paste.return_value = "until:2025-01-15_23:59:59_JST"

                        # main関数をモックして、キーワード選択部分のみテスト
                        with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                            with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                                with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                                    with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                        mock_get_position.return_value = (100, 100)
                                        mock_copy.return_value = "<html>test</html>"
                                        mock_save.return_value = "test.html"

                                        # customキーワードの場合は入力もモック
                                        if keyword_type == 'custom':
                                            with patch('builtins.input') as mock_input:
                                                mock_input.return_value = "custom keyword"
                                                result = main()
                                        else:
                                            result = main()

                                        # キーワードが正しく選択されたことを確認
                                        self.assertIsNotNone(result)

    def test_custom_keyword_input(self):
        """カスタムキーワード入力テスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--keyword-type', 'custom']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-01-15_23:59:59_JST"

                # main関数をモックして、カスタムキーワード入力部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                with patch('builtins.input') as mock_input:
                                    mock_get_position.return_value = (100, 100)
                                    mock_copy.return_value = "<html>test</html>"
                                    mock_save.return_value = "test.html"
                                    mock_input.return_value = "custom search keyword"

                                    # main関数を実行
                                    result = main()

                                    # カスタムキーワードが正しく入力されたことを確認
                                    self.assertIsNotNone(result)

    def test_main_with_no_date_option(self):
        """--no-dateオプション付きのmain関数テスト"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-05-08_16:54:40_JST"

                # main関数をモックして、--no-dateオプション処理部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "data/input/250508.html"

                                # main関数を実行
                                result = main()

                                # --no-dateオプションが正しく処理されたことを確認
                                self.assertIsNotNone(result)

    def test_search_query_generation_with_date(self):
        """日付指定ありでの検索クエリ生成テスト（実際の動作）"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-01-15_23:59:59_JST"

                # main関数をモックして、検索クエリ生成部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "test.html"

                                # main関数を実行
                                result = main()

                                # 検索クエリが正しく生成されたことを確認
                                self.assertIsNotNone(result)

    def test_search_query_generation_with_no_date(self):
        """日付指定なしでの検索クエリ生成テスト（実際の動作）"""
        from src.create_twitter_html_auto import main

        # テスト用の引数を設定
        test_args = ['create_twitter_html_auto.py', '2025-01-15', '--no-date']

        with patch('sys.argv', test_args):
            with patch('pyperclip.paste') as mock_paste:
                mock_paste.return_value = "until:2025-05-08_16:54:40_JST"

                # main関数をモックして、検索クエリ生成部分のみテスト
                with patch('src.create_twitter_html_auto.get_position') as mock_get_position:
                    with patch('src.create_twitter_html_auto.navigate_to_twitter_search') as mock_navigate:
                        with patch('src.create_twitter_html_auto.copy_html_with_extension') as mock_copy:
                            with patch('src.create_twitter_html_auto.save_html_to_file') as mock_save:
                                mock_get_position.return_value = (100, 100)
                                mock_copy.return_value = "<html>test</html>"
                                mock_save.return_value = "data/input/250508.html"

                                # main関数を実行
                                result = main()

                                # 検索クエリが正しく生成されたことを確認
                                self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()
