import unittest
import argparse
import sys
import os
from io import StringIO
from unittest.mock import patch, MagicMock, mock_open

# テスト対象のモジュールをインポート
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import parse_arguments, CustomArgumentParser

class TestNoDateOption(unittest.TestCase):
    def setUp(self):
        # 標準出力をキャプチャするための設定
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        # 標準出力を元に戻す
        sys.stdout = self.original_stdout
        self.held_output.close()

    def test_no_date_option(self):
        # テスト用の引数リスト
        test_args = ['all', '--no-date', '-k', 'manekineko']
        
        # テスト用の設定
        class TestConfig:
            KEYWORD_PREFIX_MAPPING = {
                'default': None,
                'manekineko': 'manekineko',
                'chikirin': 'chikirin'
            }
        
        # パーサーを作成
        parser = CustomArgumentParser(description='Test Parser')
        subparsers = parser.add_subparsers(dest='command')
        
        # all コマンドを追加
        all_parser = subparsers.add_parser('all')
        all_parser.add_argument('date', nargs='?', default=None)
        all_parser.add_argument('--no-date', action='store_true')
        all_parser.add_argument('-k', '--keyword-type', default='default',
                              dest='keyword_type')
        
        # 引数をパース
        args = parser.parse_args(test_args)
        
        # アサーション
        self.assertEqual(args.command, 'all')
        self.assertTrue(args.no_date)
        self.assertEqual(args.keyword_type, 'manekineko')
        self.assertIsNone(args.date)  # date は None であるべき

    def test_with_date_and_no_date_option(self):
        # テスト用の引数リスト
        test_args = ['all', '250830', '--no-date', '-k', 'manekineko']
        
        # パーサーを作成
        parser = CustomArgumentParser(description='Test Parser')
        subparsers = parser.add_subparsers(dest='command')
        
        # all コマンドを追加
        all_parser = subparsers.add_parser('all')
        all_parser.add_argument('date', nargs='?', default=None)
        all_parser.add_argument('--no-date', action='store_true')
        all_parser.add_argument('-k', '--keyword-type', default='default',
                              dest='keyword_type')
        
        # 引数をパース
        args = parser.parse_args(test_args)
        
        # アサーション
        self.assertEqual(args.command, 'all')
        self.assertTrue(args.no_date)
        self.assertEqual(args.keyword_type, 'manekineko')
        self.assertEqual(args.date, '250830')  # date は指定された値であるべき

if __name__ == '__main__':
    unittest.main()
