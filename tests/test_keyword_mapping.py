#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
キーワードマッピングのテスト
"""

import sys
import os
import unittest
from unittest.mock import patch

# プロジェクトのルートディレクトリをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from main import parse_arguments

class TestKeywordMapping(unittest.TestCase):
    """キーワードマッピングのテストケース"""
    
    def test_keyword_mapping_includes_manekineko(self):
        """manekinekoがKEYWORD_PREFIX_MAPPINGに含まれていることを確認"""
        self.assertIn('manekineko', config.KEYWORD_PREFIX_MAPPING)
        self.assertEqual(config.KEYWORD_PREFIX_MAPPING['manekineko'], 'manekineko')
    
    def test_parse_arguments_accepts_manekineko(self):
        """parse_argumentsがmanekinekoを許可することを確認"""
        test_args = ['all', '250830', '-k', 'manekineko']
        with patch('sys.argv', ['main.py'] + test_args):
            args = parse_arguments(test_args)
            self.assertEqual(args.keyword_type, 'manekineko')

if __name__ == "__main__":
    unittest.main()
