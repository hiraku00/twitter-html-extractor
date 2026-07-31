import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# モジュールのパスを追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

class TestNavigateToTwitterSearch(unittest.TestCase):
    @patch('pyautogui.click')
    @patch('pyautogui.keyDown')
    @patch('pyautogui.keyUp')
    @patch('pyautogui.press')
    @patch('pyperclip.copy')
    @patch('pyperclip.paste', return_value='test query')
    @patch('time.sleep')
    def test_navigate_to_twitter_search(self, mock_sleep, mock_paste, mock_copy,
                                        mock_press, mock_key_up, mock_key_down,
                                        mock_click):
        # テスト対象の関数を動的にインポート
        from create_twitter_html_all import navigate_to_twitter_search
        
        # テストデータ
        search_query = "test query"
        search_box_pos = {'x': 100, 'y': 200}
        
        # テスト実行
        navigate_to_twitter_search(search_query, search_box_pos)
        
        # 検証
        # 1. 検索欄へのフォーカス、×ボタンでのクリア、貼り付け前の再フォーカス
        self.assertEqual(mock_click.call_count, 3)
        mock_click.assert_any_call(100, 200)
        
        # 2. クリップボードにコピー
        mock_copy.assert_called_once_with("test query")
        
        # 3. Commandを押した状態でvを送り、確実に解放する
        mock_key_down.assert_any_call('command')
        mock_key_up.assert_any_call('command')
        mock_press.assert_any_call('v')
        
        # 4. 残ったポップアップを閉じてからEnterキー
        mock_press.assert_any_call('esc')
        mock_press.assert_any_call('enter')
        
        # 5. スリープの呼び出しを確認
        mock_sleep.assert_called()

if __name__ == '__main__':
    unittest.main()
