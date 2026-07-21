"""ちきりんセレクトTVの取得結果をObsidianの視聴リストへ追記する。"""

from datetime import datetime
from pathlib import Path
import re


WATCH_LIST_PATH = Path(
    "/Users/hiraku/Obsidian/hiraku-local/04_watch-list/"
    "watch list (text, audio, movie).md"
)


def _escape_markdown_cell(value):
    """Markdown表のセルとして安全な文字列にする。"""
    return re.sub(r"\s+", " ", str(value or "")).strip().replace("|", "\\|")


def _watch_date(datetime_value):
    """抽出した日時を既存表の M/D 表記に変換する。"""
    try:
        return datetime.strptime(datetime_value, "%Y/%m/%d %H:%M:%S").strftime("%-m/%-d")
    except (TypeError, ValueError):
        return ""


def _make_row(tweet):
    """ツイート1件を既存の11列のMarkdown表行へ変換する。"""
    text = _escape_markdown_cell(tweet.get("text"))
    url = _escape_markdown_cell(tweet.get("quote_url"))
    x_link = f"[X]({url})" if url else ""
    cells = [
        "ちきりん",
        _watch_date(tweet.get("datetime")),
        "movie",
        "",
        text,
        "",
        "",
        "",
        x_link,
        "",
        "",
    ]
    return "| " + " | ".join(cells) + " |\n"


def append_chikirin_tweets(tweets, watch_list_path=WATCH_LIST_PATH):
    """未登録のちきりん投稿を視聴リストの空行の前へ追記する。

    Returns:
        int: 実際に追記した投稿数。
    """
    path = Path(watch_list_path)
    if not path.exists():
        raise FileNotFoundError(f"視聴リストが見つかりません: {path}")

    content = path.read_text(encoding="utf-8")
    existing_urls = set(re.findall(r"https?://[^)\s<]+", content))
    new_tweets = []
    seen_urls = set()

    for tweet in tweets:
        url = (tweet.get("quote_url") or "").strip()
        if not url or url in existing_urls or url in seen_urls:
            continue
        seen_urls.add(url)
        new_tweets.append(tweet)

    if not new_tweets:
        return 0

    rows = "".join(_make_row(tweet) for tweet in new_tweets)
    lines = content.splitlines(keepends=True)
    insert_at = len(lines)
    for index, line in enumerate(lines):
        if re.fullmatch(r"\|\s*(?:\|\s*){11}\n?", line):
            insert_at = index
            break
    lines.insert(insert_at, rows)
    path.write_text("".join(lines), encoding="utf-8")
    return len(new_tweets)
