import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from append_chikirin_to_watch_list import append_chikirin_tweets


class TestAppendChikirinToWatchList(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False)
        self.temp_file.write(
            "| person | create<br>date | type | title | contents | pri | watch<br>date | status | URL | comment | |\n"
            "| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | --- |\n"
            "| 既存 | | movie | | | | | | [X](https://x.com/a/status/1) | | |\n"
            "| | | | | | | | | | | |\n"
        )
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def test_appends_new_tweets_before_empty_rows_and_skips_duplicates(self):
        tweets = [
            {
                "datetime": "2026/07/20 18:53:32",
                "text": "番組の感想 | 補足\n改行あり",
                "quote_url": "https://x.com/InsideCHIKIRIN/status/2",
            },
            {
                "datetime": "2026/07/20 18:54:50",
                "text": "既存投稿",
                "quote_url": "https://x.com/a/status/1",
            },
        ]

        self.assertEqual(append_chikirin_tweets(tweets, self.temp_file.name), 1)
        self.assertEqual(append_chikirin_tweets(tweets, self.temp_file.name), 0)

        with open(self.temp_file.name, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("| ちきりん | 7/20 | movie |  | 番組の感想 \\| 補足 改行あり", content)
        self.assertLess(content.index("InsideCHIKIRIN/status/2"), content.index("| | | | | | | | | | | |"))
