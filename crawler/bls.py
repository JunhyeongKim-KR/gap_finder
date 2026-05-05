"""BLS — 미국 노동통계국.

Endpoint: https://api.bls.gov/publicAPI/v2/timeseries/data/
Doc: https://www.bls.gov/developers/api_signature_v2.htm

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"


def _key() -> str:
    k = os.getenv("BLS_API_KEY", "")
    if not k:
        raise RuntimeError("BLS_API_KEY 가 .env 에 설정되지 않음")
    return k


def get_series(series_ids: list[str], start_year: int, end_year: int) -> dict:
    """시계열 조회. 예: series_ids=['CUUR0000SA0'] (CPI)."""
    payload = {
        "seriesid": series_ids,
        "startyear": str(start_year),
        "endyear": str(end_year),
        "registrationkey": _key(),
    }
    r = requests.post(BASE_URL, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()
