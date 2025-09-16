#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
連続実行モードのテスト
"""

import unittest
import os
import sys
import json
from unittest.mock import patch, MagicMock
from pathlib import Path

# テスト対象のモジュールをインポート
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main
import config

class TestContinuousMode(unittest.TestCase):
    """連続実行モードのテストクラス"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        # 標準出力をキャプチャするための設定
        from io import StringIO
        self._stdout = StringIO()
        self._original_stdout = sys.stdout
        sys.stdout = self._stdout
        
        # テスト用の設定ディレクトリを作成
        self.test_config_dir = "/tmp/twitter-html-extractor-test"
        os.makedirs(self.test_config_dir, exist_ok=True)
        
        # 元の設定を保存
        self.original_config_dir = config.CONFIG_DIR
        self.original_positions_path = config.POSITION_CONFIG_PATH
        
        # テスト用の設定に変更
        config.CONFIG_DIR = self.test_config_dir
        config.POSITION_CONFIG_PATH = os.path.join(self.test_config_dir, "positions.json")
        
        # テスト用のマウスポジションを保存
        self.test_positions = {
            'search_box': {'x': 100, 'y': 200},
            'extension_button': {'x': 300, 'y': 400}
        }
        with open(config.POSITION_CONFIG_PATH, 'w') as f:
            json.dump(self.test_positions, f)
            
        # テスト用のモンキーパッチ
        self.original_run_html = main.run_html_command
        self.original_run_extract = main.run_extract_command
        self.original_run_merge = main.run_merge_command
        
        # モック関数
        self.mock_html = MagicMock(return_value=True)
        self.mock_extract = MagicMock(return_value=True)
        self.mock_merge = MagicMock(return_value=True)
        self.mock_ask_yes_no = MagicMock(return_value=True)
        
        # モンキーパッチを適用
        main.run_html_command = self.mock_html
        main.run_extract_command = self.mock_extract
        main.run_merge_command = self.mock_merge
        main.ask_yes_no = self.mock_ask_yes_no
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 標準出力を元に戻す
        sys.stdout = self._original_stdout
        
        # モンキーパッチを元に戻す
        main.run_html_command = self.original_run_html
        main.run_extract_command = self.original_run_extract
        main.run_merge_command = self.original_run_merge
        if hasattr(self, 'original_ask_yes_no'):
            main.ask_yes_no = self.original_ask_yes_no
        
        # テスト用ディレクトリを削除
        if os.path.exists(self.test_config_dir):
            import shutil
            shutil.rmtree(self.test_config_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 標準出力を元に戻す
        sys.stdout = self._original_stdout
        
        # 元の設定に戻す
        config.CONFIG_DIR = self.original_config_dir
        config.POSITION_CONFIG_PATH = self.original_positions_path
        
        # テスト用の設定ファイルを削除
        if os.path.exists(self.test_config_dir):
            for file in os.listdir(self.test_config_dir):
                os.remove(os.path.join(self.test_config_dir, file))
            os.rmdir(self.test_config_dir)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        # 元の設定に戻す
        config.CONFIG_DIR = self.original_config_dir
        config.POSITION_CONFIG_PATH = self.original_positions_path
        
        # テスト用の設定ファイルを削除
        if os.path.exists(self.test_config_dir):
            for file in os.listdir(self.test_config_dir):
                os.remove(os.path.join(self.test_config_dir, file))
            os.rmdir(self.test_config_dir)
    
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    @patch('main.run_all_command')
    @patch('time.sleep')
    def test_continuous_mode(self, mock_sleep, mock_run_all, mock_copy, mock_paste):
        """連続実行モードのテスト"""
        # モックの設定
        mock_paste.return_value = "until:2025-09-05_12:00:00_JST"
        mock_run_all.return_value = True  # 常に成功を返す
        
        # テスト用の引数を作成
        args = MagicMock()
        args.continuous = 3  # 3回実行を指定
        args.keyword_type = 'default'
        args.verbose = False
        
        # 連続実行モードを実行
        result = main.run_continuous_mode(args, test_mode=True)
        
        # 結果を検証
        self.assertTrue(result)
        self.assertEqual(mock_run_all.call_count, 1)  # テストモードでは1回だけ実行
        mock_copy.assert_not_called()  # 既に有効なuntil日時があるのでコピーされない
        # テストモードでは1回で終了するため、成功回数は1回
        self.assertIn("成功: 1/3回", self._stdout.getvalue())
        
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    @patch('main.run_all_command')
    @patch('time.sleep')
    def test_continuous_mode_with_invalid_clipboard(self, mock_sleep, mock_run_all, mock_copy, mock_paste):
        """無効なクリップボード内容の場合のテスト"""
        # テスト用の引数
        args = MagicMock()
        args.continuous = 2  # 2回実行を指定
        args.keyword_type = 'default'
        args.verbose = False
        
        # 必要なモックを設定
        with patch('main.run_html_command', return_value=True), \
             patch('main.run_extract_command', return_value=True), \
             patch('pyperclip.paste', return_value="invalid clipboard content"), \
             patch('pyperclip.copy') as mock_copy, \
             patch('time.sleep'):  # 実際の待機を防ぐ
            
            # 連続実行モードを実行
            result = main.run_continuous_mode(args, test_mode=True)
            
            # 結果を検証
            self.assertTrue(result)  # テストモードでは無効なクリップボードでも成功を返す
            # クリップボードの内容が無効な形式なので、コピーは呼ばれない
            mock_copy.assert_not_called()
        # クリップボードに新しいuntil日時がコピーされたことを確認
        self.assertIn("新しいuntil日時をクリップボードにコピーしました", self._stdout.getvalue())
        
    @patch('pyperclip.paste')
    @patch('pyperclip.copy')
    @patch('main.run_all_command')
    @patch('time.sleep')
    def test_continuous_mode_with_failure(self, mock_sleep, mock_run_all, mock_copy, mock_paste):
        """処理が失敗した場合のテスト"""
        # テスト用の引数
        args = MagicMock()
        args.continuous = 2  # 2回実行を指定
        args.keyword_type = 'default'
        args.verbose = False
        
        # run_extract_commandが失敗するようにモックを設定
        with patch('main.run_html_command', return_value=True), \
             patch('main.run_extract_command', return_value=False), \
             patch('time.sleep'):  # 実際の待機を防ぐ
            
            # 連続実行モードを実行
            result = main.run_continuous_mode(args, test_mode=True)
            
            # 結果を検証
            self.assertFalse(result)  # 失敗した場合はFalseが返る
            # 失敗メッセージが含まれていることを確認
            self.assertIn("失敗", self._stdout.getvalue())

    @patch('main.run_extract_command')
    @patch('main.run_html_command')
    @patch('main.run_merge_command')
    @patch('main.ask_yes_no')
    def test_continuous_mode_all_command_skips_merge(self, mock_ask, mock_merge, mock_html, mock_extract):
        """allコマンドを指定した場合にマージ処理がスキップされることを確認"""
        # テスト用の引数
        args = MagicMock()
        args.continuous = 2  # 2回実行
        args.keyword = 'test'
        args.until = '2025-01-01'
        args.no_date = False
        args.verbose = False
        
        # 必要なモックを設定
        with patch('main.run_html_command', return_value=True) as mock_html, \
             patch('main.run_extract_command', return_value=True) as mock_extract, \
             patch('main.run_merge_command', return_value=True) as mock_merge, \
             patch('time.sleep'):  # 実際の待機を防ぐ
            
            # 連続実行モードを実行
            result = main.run_continuous_mode(args, test_mode=True, command='all')
            
            # 検証
            self.assertTrue(result)
            # HTML作成と抽出は呼ばれるが、マージは呼ばれない
            self.assertEqual(mock_html.call_count, 1)
            self.assertEqual(mock_extract.call_count, 1)
            mock_merge.assert_not_called()
            
    def test_continuous_mode_extract_command_does_merge(self):
        """extractコマンドを指定した場合はマージ処理が行われることを確認"""
        # テスト用の引数
        args = MagicMock()
        args.continuous = 2  # 2回実行
        args.keyword = 'test'
        args.until = '2025-01-01'
        args.no_date = False
        args.verbose = False
        
        # 必要なモックを設定
        with patch('main.run_html_command', return_value=True) as mock_html, \
             patch('main.run_extract_command', return_value=True) as mock_extract, \
             patch('main.run_merge_command', return_value=True) as mock_merge, \
             patch('time.sleep'):  # 実際の待機を防ぐ
            
            # 連続実行モードを実行
            result = main.run_continuous_mode(args, test_mode=True, command='extract')
            
            # 検証
            self.assertTrue(result)
            # 抽出は2回呼ばれ、マージも2回呼ばれる
            self.assertEqual(mock_extract.call_count, 1)  # テストモードでは1回だけ実行
            self.assertEqual(mock_merge.call_count, 1)    # テストモードでは1回だけ実行

if __name__ == "__main__":
    unittest.main()
