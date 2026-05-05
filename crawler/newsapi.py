"""NewsAPI — 글로벌 뉴스.

Endpoint: https://newsapi.org/v2/
Doc: https://newsapi.org/docs

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://newsapi.org/v2"


def _key() -> str:
    k = os.getenv("NEWSAPI_KEY", "")
    if not k:
        raise RuntimeError("NEWSAPI_KEY 가 .env 에 설정되지 않음")
    return k


def everything(query: str, **params: object) -> dict:
    p = {"q": query, "apiKey": _key(), **params}
    r = requests.get(f"{BASE_URL}/everything", params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def top_headlines(**params: object) -> dict:
    p = {"apiKey": _key(), **params}
    r = requests.get(f"{BASE_URL}/top-headlines", params=p, timeout=30)
    r.raise_for_status()
    return r.json()
