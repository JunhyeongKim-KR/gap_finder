"""Polygon.io — 미국 주식 시세·옵션·crypto.

Endpoint: https://api.polygon.io/
Doc: https://polygon.io/docs

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://api.polygon.io"


def _key() -> str:
    k = os.getenv("POLYGON_API_KEY", "")
    if not k:
        raise RuntimeError("POLYGON_API_KEY 가 .env 에 설정되지 않음")
    return k


def aggregates(symbol: str, multiplier: int, timespan: str, from_date: str, to_date: str) -> dict:
    """OHLCV. timespan: minute/hour/day/week/month. from/to: YYYY-MM-DD."""
    url = f"{BASE_URL}/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{from_date}/{to_date}"
    r = requests.get(url, params={"apiKey": _key()}, timeout=30)
    r.raise_for_status()
    return r.json()


def ticker_details(symbol: str) -> dict:
    r = requests.get(
        f"{BASE_URL}/v3/reference/tickers/{symbol}", params={"apiKey": _key()}, timeout=30
    )
    r.raise_for_status()
    return r.json()


def news(symbol: str, limit: int = 50) -> dict:
    r = requests.get(
        f"{BASE_URL}/v2/reference/news",
        params={"ticker": symbol, "limit": limit, "apiKey": _key()},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()
