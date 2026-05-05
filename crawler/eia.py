"""EIA — 미국 에너지정보국.

Endpoint: https://api.eia.gov/v2/
Doc: https://www.eia.gov/opendata/

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://api.eia.gov/v2"


def _key() -> str:
    k = os.getenv("EIA_API_KEY", "")
    if not k:
        raise RuntimeError("EIA_API_KEY 가 .env 에 설정되지 않음")
    return k


def get_series(route: str, **params: object) -> dict:
    """EIA v2 API 호출. 예: route='petroleum/pri/spt/data/'."""
    url = f"{BASE_URL}/{route.strip('/')}/"
    p = {"api_key": _key(), **params}
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()
