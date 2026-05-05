"""data.go.kr — 한국 공공데이터포털.

Endpoint: 각 데이터셋별 상이 (https://www.data.go.kr/)
Doc: https://www.data.go.kr/index.do

Phase A skeleton — 단일 endpoint 가 아니라 각 dataset 별로 base URL 이 다름.
"""
from __future__ import annotations

import os

import requests


def _key() -> str:
    k = os.getenv("DATA_GO_KR_API_KEY", "")
    if not k:
        raise RuntimeError("DATA_GO_KR_API_KEY 가 .env 에 설정되지 않음")
    return k


def call(endpoint_url: str, **params: object) -> dict:
    """공공데이터포털 단건 호출. 일부 endpoint 는 serviceKey 파라미터명."""
    p = {"serviceKey": _key(), **params}
    r = requests.get(endpoint_url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()
