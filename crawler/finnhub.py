"""Finnhub — 글로벌 종목·뉴스·재무.

Endpoint: https://finnhub.io/api/v1/
Doc: https://finnhub.io/docs/api

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://finnhub.io/api/v1"


def _key() -> str:
    k = os.getenv("FINNHUB_API_KEY", "")
    if not k:
        raise RuntimeError("FINNHUB_API_KEY 가 .env 에 설정되지 않음")
    return k


def quote(symbol: str) -> dict:
    r = requests.get(f"{BASE_URL}/quote", params={"symbol": symbol, "token": _key()}, timeout=30)
    r.raise_for_status()
    return r.json()


def company_news(symbol: str, from_date: str, to_date: str) -> list[dict]:
    """뉴스. from/to: YYYY-MM-DD."""
    r = requests.get(
        f"{BASE_URL}/company-news",
        params={"symbol": symbol, "from": from_date, "to": to_date, "token": _key()},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def basic_financials(symbol: str, metric: str = "all") -> dict:
    r = requests.get(
        f"{BASE_URL}/stock/metric",
        params={"symbol": symbol, "metric": metric, "token": _key()},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def earnings(symbol: str) -> list[dict]:
    r = requests.get(
        f"{BASE_URL}/stock/earnings", params={"symbol": symbol, "token": _key()}, timeout=30
    )
    r.raise_for_status()
    return r.json()
