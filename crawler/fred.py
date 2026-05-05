"""FRED — 미국 연준 거시 통계.

Endpoint: https://api.stlouisfed.org/fred/
Doc: https://fred.stlouisfed.org/docs/api/fred/

Phase A skeleton.
"""
from __future__ import annotations

import os
from typing import Any

import requests

BASE_URL = "https://api.stlouisfed.org/fred"


def _key() -> str:
    k = os.getenv("FRED_API_KEY", "")
    if not k:
        raise RuntimeError("FRED_API_KEY 가 .env 에 설정되지 않음")
    return k


def get_series(series_id: str, **params: Any) -> dict:
    """시계열 관측치 조회. 예: series_id='GDP', 'CPIAUCSL', 'DGS10'."""
    url = f"{BASE_URL}/series/observations"
    p = {"series_id": series_id, "api_key": _key(), "file_type": "json", **params}
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def search_series(query: str, limit: int = 20) -> dict:
    url = f"{BASE_URL}/series/search"
    p = {"search_text": query, "api_key": _key(), "file_type": "json", "limit": limit}
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()
