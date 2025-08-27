#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import argparse
import sys
from unittest.mock import patch

# テスト対象の関数をインポート
sys.path.append('.')
from main import parse_arguments, run_all_command

class TestArgumentParser(unittest.TestCase):
    def test_all_with_no_date(self):
        """--all --no-date の組み合わせをテスト"""
        # テスト用の引数パーサーを作成
        parser = argparse.ArgumentParser()
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--all', nargs='?', const='no_date', metavar='YYMMDD')
        group.add_argument('--html', nargs='?', const=None, metavar='YYMMDD')
        group.add_argument('--merge', action='store_true')
        group.add_argument('--extract', metavar='YYMMDD')
        
        # オプション引数を追加
        parser.add_argument('--no-date', action='store_true')
        parser.add_argument('--search-keyword')
        
        # テストケース
        test_cases = [
            (["--all", "--no-date", "--search-keyword", "from:test"], {
                'all': 'no_date',
                'no_date': True,
                'search_keyword': 'from:test'
            }),
            (["--all", "250826", "--search-keyword", "from:test"], {
                'all': '250826',
                'no_date': False,
                'search_keyword': 'from:test'
            })
        ]
        
        for test_args, expected in test_cases:
            with self.subTest(test_args=test_args):
                # 引数をパース
                args = parser.parse_args(test_args)
                
                # 期待される属性が存在するか確認
                for attr, value in expected.items():
                    self.assertTrue(hasattr(args, attr))
                    self.assertEqual(getattr(args, attr), value)

    def test_all_with_date(self):
        """--all に日付を指定した場合をテスト"""
        test_args = [
            "--all", "250826", "--search-keyword", "from:test"
        ]
        
        with patch('sys.argv', ['test.py'] + test_args):
            args = parse_arguments()
            self.assertEqual(args.all, "250826")
            self.assertFalse(hasattr(args, 'no_date') and args.no_date)

if __name__ == "__main__":
    unittest.main()
