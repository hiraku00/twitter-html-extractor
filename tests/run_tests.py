#!/usr/bin/env python3
"""
Test Runner for Twitter HTML Extractor
"""

import unittest
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """全テストを実行"""
    # テストディスカバリー
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')

    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 結果を返す
    return result.wasSuccessful()

if __name__ == '__main__':
    print("Twitter HTML Extractor - Test Suite")
    print("=" * 50)

    success = run_all_tests()

    if success:
        print("\n✅ 全テストが成功しました！")
        sys.exit(0)
    else:
        print("\n❌ 一部のテストが失敗しました。")
        sys.exit(1)
