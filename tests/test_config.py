#!/usr/bin/env python3
"""
設定ファイルのテスト
"""

import unittest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import config

class TestConfig(unittest.TestCase):

    def test_search_keywords_exist(self):
        """検索キーワードが定義されていることを確認"""
        self.assertIn('default', config.SEARCH_KEYWORDS)
        self.assertIn('thai', config.SEARCH_KEYWORDS)
        self.assertIn('en', config.SEARCH_KEYWORDS)
        self.assertIn('chikirin', config.SEARCH_KEYWORDS)
        self.assertIn('custom', config.SEARCH_KEYWORDS)

    def test_keyword_prefix_mapping(self):
        """キーワードタイプとprefixのマッピングが正しく設定されていることを確認"""
        self.assertIn('default', config.KEYWORD_PREFIX_MAPPING)
        self.assertIn('thai', config.KEYWORD_PREFIX_MAPPING)
        self.assertIn('en', config.KEYWORD_PREFIX_MAPPING)
        self.assertIn('chikirin', config.KEYWORD_PREFIX_MAPPING)
        self.assertIn('custom', config.KEYWORD_PREFIX_MAPPING)

        # chikirinのprefixが正しく設定されていることを確認
        self.assertEqual(config.KEYWORD_PREFIX_MAPPING['chikirin'], 'chikirin')

        # 他のキーワードタイプはprefixがNoneであることを確認
        self.assertIsNone(config.KEYWORD_PREFIX_MAPPING['default'])
        self.assertIsNone(config.KEYWORD_PREFIX_MAPPING['thai'])
        self.assertIsNone(config.KEYWORD_PREFIX_MAPPING['en'])
        self.assertIsNone(config.KEYWORD_PREFIX_MAPPING['custom'])

    def test_get_prefix_folders(self):
        """prefix別フォルダ取得機能のテスト"""
        # prefixなしの場合
        folders = config.get_prefix_folders(None)
        self.assertEqual(folders['input'], config.INPUT_FOLDER)
        self.assertEqual(folders['output'], config.OUTPUT_FOLDER)
        self.assertEqual(folders['txt'], config.TXT_OUTPUT_FOLDER)
        self.assertEqual(folders['json'], config.JSON_OUTPUT_FOLDER)
        self.assertEqual(folders['csv'], config.CSV_OUTPUT_FOLDER)

        # chikirin prefixの場合
        folders = config.get_prefix_folders('chikirin')
        self.assertEqual(folders['input'], 'data/input/chikirin')
        self.assertEqual(folders['output'], 'data/output/chikirin')
        self.assertEqual(folders['txt'], 'data/output/chikirin/txt')
        self.assertEqual(folders['json'], 'data/output/chikirin/json')
        self.assertEqual(folders['csv'], 'data/output/chikirin/csv')

    def test_default_search_keyword(self):
        """デフォルト検索キーワードが設定されていることを確認"""
        self.assertIsNotNone(config.DEFAULT_SEARCH_KEYWORD)
        self.assertIsInstance(config.DEFAULT_SEARCH_KEYWORD, str)
        self.assertGreater(len(config.DEFAULT_SEARCH_KEYWORD), 0)

    def test_file_paths_exist(self):
        """ファイルパスが定義されていることを確認"""
        self.assertIsNotNone(config.INPUT_FOLDER)
        self.assertIsNotNone(config.OUTPUT_FOLDER)
        self.assertIsNotNone(config.TXT_OUTPUT_FOLDER)
        self.assertIsNotNone(config.JSON_OUTPUT_FOLDER)
        self.assertIsNotNone(config.CSV_OUTPUT_FOLDER)

    def test_search_query_templates_exist(self):
        """検索クエリテンプレートが定義されていることを確認"""
        self.assertIsNotNone(config.SEARCH_QUERY_TEMPLATE_WITH_SINCE)
        self.assertIsNotNone(config.SEARCH_QUERY_TEMPLATE_WITHOUT_SINCE)
        self.assertIn('{date}', config.SEARCH_QUERY_TEMPLATE_WITH_SINCE)
        self.assertIn('{keyword}', config.SEARCH_QUERY_TEMPLATE_WITH_SINCE)
        self.assertIn('{keyword}', config.SEARCH_QUERY_TEMPLATE_WITHOUT_SINCE)

    def test_date_format_exists(self):
        """日付形式が定義されていることを確認"""
        self.assertIsNotNone(config.DATE_FORMAT)
        self.assertIsNotNone(config.TIME_FORMAT)

    def test_debug_setting_exists(self):
        """デバッグ設定が定義されていることを確認"""
        self.assertIsInstance(config.DEBUG, bool)

if __name__ == '__main__':
    unittest.main()
