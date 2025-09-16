import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# モジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestNavigateToTwitterSearch(unittest.TestCase):
    @patch('pyautogui.click')
    @patch('pyautogui.hotkey')
    @patch('pyautogui.press')
    @patch('pyperclip.copy')
    @patch('time.sleep')
    def test_navigate_to_twitter_search(self, mock_sleep, mock_copy, mock_press, mock_hotkey, mock_click):
        # テスト対象の関数を動的にインポート
        from create_twitter_html_all import navigate_to_twitter_search
        
        # テストデータ
        search_query = "test query"
        search_box_pos = {'x': 100, 'y': 200}
        
        # テスト実行
        navigate_to_twitter_search(search_query, search_box_pos)
        
        # 検証
        # 1. 検索ボックスを2回クリック
        self.assertEqual(mock_click.call_count, 2)
        mock_click.assert_any_call(100, 200)
        
        # 2. クリップボードにコピー
        mock_copy.assert_called_once_with("test query")
        
        # 3. ペースト
        mock_hotkey.assert_called_once_with('command', 'v')
        
        # 4. Enterキー
        mock_press.assert_called_once_with('enter')
        
        # 5. スリープの呼び出しを確認
        mock_sleep.assert_called()

if __name__ == '__main__':
    unittest.main()
