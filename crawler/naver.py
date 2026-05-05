"""Naver Search API — 한국 뉴스·블로그·검색.

Endpoint: https://openapi.naver.com/v1/search/{type}
Doc: https://developers.naver.com/docs/serviceapi/search/

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://openapi.naver.com/v1/search"


def _headers() -> dict[str, str]:
    cid = os.getenv("NAVER_CLIENT_ID", "")
    sec = os.getenv("NAVER_CLIENT_SECRET", "")
    if not (cid and sec):
        raise RuntimeError("NAVER_CLIENT_ID / NAVER_CLIENT_SECRET 가 .env 에 설정되지 않음")
    return {"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": sec}


def search(kind: str, query: str, display: int = 30, start: int = 1, sort: str = "date") -> dict:
    """kind: news/blog/cafearticle/webkr/shop/encyc/book. sort: sim|date."""
    url = f"{BASE_URL}/{kind}.json"
    p = {"query": query, "display": display, "start": start, "sort": sort}
    r = requests.get(url, headers=_headers(), params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def news(query: str, **params: object) -> dict:
    return search("news", query, **params)


def blog(query: str, **params: object) -> dict:
    return search("blog", query, **params)
