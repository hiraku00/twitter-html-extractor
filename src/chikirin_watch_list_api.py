"""ちきりんセレクトTVの取得結果をdashboardのwatch-list APIへ登録する処理。"""

from __future__ import annotations

import json
import os
import re
import ssl
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

import certifi
from dotenv import load_dotenv

SOURCE_SYSTEM = "chikirin"


class WatchListApiError(RuntimeError):
    """watch-list APIとの通信または応答に関するエラー。"""


def append_chikirin_tweets_to_dashboard(
    tweets: Iterable[dict], *, api_url: str | None = None
) -> dict[str, int]:
    """未登録のちきりん投稿をdashboardのwatch-list APIへ追加し、登録結果を返す。"""
    load_dotenv()
    base_url = _base_api_url(api_url or os.environ.get("WATCH_LIST_API_URL", ""))
    if not base_url:
        raise WatchListApiError("WATCH_LIST_API_URLが設定されていません")

    candidates = _to_api_items(tweets)
    if not candidates:
        return {"created": 0, "skipped": 0, "errors": 0}

    existing_external_ids = _fetch_existing_external_ids(base_url)
    filtered = [item for item in candidates if item["externalId"] not in existing_external_ids]
    skipped = len(candidates) - len(filtered)

    created = 0
    errors = 0
    for start in range(0, len(filtered), 200):
        result = _post_import(base_url, filtered[start : start + 200])
        created += int(result.get("created", 0))
        messages = result.get("messages", [])
        errors += int(result.get("errors", 0))
        skipped += sum(1 for message in messages if "スキップ" in str(message.get("error", "")))

    return {"created": created, "skipped": skipped, "errors": errors}


def _to_api_items(tweets: Iterable[dict]) -> list[dict]:
    items = []
    seen_urls = set()
    for tweet in tweets:
        url = (tweet.get("quote_url") or "").strip()
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        added_on = _added_on(tweet.get("datetime"))
        items.append(
            {
                "contentType": "movie",
                "creatorName": "ちきりん",
                "seriesTitle": "ちきりんセレクトTV",
                "title": _single_line(tweet.get("text")),
                "description": tweet.get("user_name") or "",
                "status": "backlog",
                "addedOn": added_on,
                "sourceSystem": SOURCE_SYSTEM,
                "externalId": url,
                "rawSource": json.dumps(tweet, ensure_ascii=False),
                "links": [{"label": "X", "url": url, "linkType": "reference"}],
            }
        )
    return items


def _single_line(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _added_on(datetime_value: str) -> str:
    match = re.match(r"(\d{4})/(\d{2})/(\d{2})", str(datetime_value or ""))
    if not match:
        return ""
    year, month, day = match.groups()
    return f"{year}-{month}-{day}"


def _fetch_existing_external_ids(base_url: str) -> set[str]:
    """既存のchikirinデータのexternalIdを取得する。"""
    external_ids = set()
    offset = 0
    while True:
        payload = _request_json(
            f"{base_url}/api/items?limit=100&offset={offset}", method="GET"
        )
        items = payload.get("items", [])
        for item in items:
            if item.get("sourceSystem") == SOURCE_SYSTEM and item.get("externalId"):
                external_ids.add(item["externalId"])
        pagination = payload.get("pagination", {})
        if not pagination.get("hasMore") or not items:
            break
        offset += len(items)
    return external_ids


def _post_import(base_url: str, items: list[dict]) -> dict:
    return _request_json(
        f"{base_url}/api/imports",
        method="POST",
        payload={"sourceName": "twitter-html-extractor-chikirin", "items": items},
    )


def _request_json(url: str, *, method: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = Request(
        url,
        data=body,
        method=method,
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": "twitter-html-extractor/1.0",
        },
    )
    client_id = _access_credential("WATCH_LIST_ACCESS_CLIENT_ID", "CF-Access-Client-Id")
    client_secret = _access_credential(
        "WATCH_LIST_ACCESS_CLIENT_SECRET", "CF-Access-Client-Secret"
    )
    if client_id and client_secret:
        request.add_header("CF-Access-Client-Id", client_id)
        request.add_header("CF-Access-Client-Secret", client_secret)

    try:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        with urlopen(request, timeout=20, context=ssl_context) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        raise WatchListApiError(f"watch-list APIがHTTP {error.code}を返しました: {detail}") from error
    except (URLError, TimeoutError, OSError) as error:
        raise WatchListApiError(f"watch-list APIへの接続に失敗しました: {error}") from error

    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise WatchListApiError("watch-list APIの応答がJSONではありません") from error
    if not isinstance(value, dict):
        raise WatchListApiError("watch-list APIの応答形式が不正です")
    return value


def _access_credential(name: str, header_name: str) -> str:
    """環境変数からAccess認証値を取得する（ヘッダー名付き入力にも対応）。"""
    value = os.environ.get(name, "").strip()
    prefix = f"{header_name}:"
    if value.lower().startswith(prefix.lower()):
        value = value[len(prefix) :].strip()
    return value


def _base_api_url(value: str) -> str:
    """APIのホストURLだけを取り出し、クエリや末尾スラッシュを除去する。"""
    parsed = urlsplit(value.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))
