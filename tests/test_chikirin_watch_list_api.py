import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from chikirin_watch_list_api import WatchListApiError, append_chikirin_tweets_to_dashboard


def _make_response(payload):
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__.return_value = response
    response.__exit__.return_value = False
    return response


class TestAppendChikirinTweetsToDashboard(unittest.TestCase):
    def setUp(self):
        os.environ["WATCH_LIST_API_URL"] = "https://dashboard.example.com"
        os.environ.pop("WATCH_LIST_ACCESS_CLIENT_ID", None)
        os.environ.pop("WATCH_LIST_ACCESS_CLIENT_SECRET", None)

    def tearDown(self):
        os.environ.pop("WATCH_LIST_API_URL", None)

    @patch("chikirin_watch_list_api.urlopen")
    def test_registers_new_tweets_and_skips_duplicates(self, mock_urlopen):
        existing_items_response = _make_response(
            {
                "items": [
                    {
                        "sourceSystem": "chikirin",
                        "externalId": "https://x.com/InsideCHIKIRIN/status/1",
                    }
                ],
                "pagination": {"hasMore": False},
            }
        )
        import_response = _make_response({"created": 1, "messages": []})
        mock_urlopen.side_effect = [existing_items_response, import_response]

        tweets = [
            {
                "datetime": "2026/07/20 18:53:32",
                "text": "番組の感想\n改行あり",
                "user_name": "InsideCHIKIRIN",
                "quote_url": "https://x.com/InsideCHIKIRIN/status/2",
            },
            {
                "datetime": "2026/07/19 10:00:00",
                "text": "既存投稿",
                "quote_url": "https://x.com/InsideCHIKIRIN/status/1",
            },
        ]

        result = append_chikirin_tweets_to_dashboard(tweets)

        self.assertEqual(result, {"created": 1, "skipped": 1, "errors": 0})

        import_request = mock_urlopen.call_args_list[1][0][0]
        body = json.loads(import_request.data.decode("utf-8"))
        self.assertEqual(body["sourceName"], "twitter-html-extractor-chikirin")
        self.assertEqual(len(body["items"]), 1)
        item = body["items"][0]
        self.assertEqual(item["contentType"], "movie")
        self.assertEqual(item["creatorName"], "ちきりん")
        self.assertEqual(item["sourceSystem"], "chikirin")
        self.assertEqual(item["externalId"], "https://x.com/InsideCHIKIRIN/status/2")
        self.assertEqual(item["title"], "番組の感想 改行あり")
        self.assertEqual(item["addedOn"], "2026-07-20")

    def test_raises_when_api_url_missing(self):
        os.environ["WATCH_LIST_API_URL"] = ""
        with self.assertRaises(WatchListApiError):
            append_chikirin_tweets_to_dashboard([{"quote_url": "https://x.com/a/status/1"}])

    def test_returns_zero_counts_when_no_tweets_have_urls(self):
        result = append_chikirin_tweets_to_dashboard([{"quote_url": ""}])
        self.assertEqual(result, {"created": 0, "skipped": 0, "errors": 0})


if __name__ == "__main__":
    unittest.main()
