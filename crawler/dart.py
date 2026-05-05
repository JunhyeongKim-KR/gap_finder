"""DART — 금융감독원 전자공시.

Endpoint: https://opendart.fss.or.kr/api/
Doc: https://opendart.fss.or.kr/intro/main.do

Phase A skeleton.
"""
from __future__ import annotations

import os
from typing import Any

import requests

BASE_URL = "https://opendart.fss.or.kr/api"


def _key() -> str:
    k = os.getenv("DART_API_KEY", "")
    if not k:
        raise RuntimeError("DART_API_KEY 가 .env 에 설정되지 않음")
    return k


def list_disclosures(corp_code: str, **params: Any) -> dict:
    """기업 공시 목록 조회. corp_code: DART 기업 고유번호."""
    url = f"{BASE_URL}/list.json"
    p = {"crtfc_key": _key(), "corp_code": corp_code, **params}
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def get_company(corp_code: str) -> dict:
    """기업 기본 정보."""
    url = f"{BASE_URL}/company.json"
    p = {"crtfc_key": _key(), "corp_code": corp_code}
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def get_financial_statement(corp_code: str, year: int, reprt_code: str = "11011") -> dict:
    """재무제표 단일회사 조회. reprt_code: 11011=사업, 11012=반기, 11013=1Q, 11014=3Q."""
    url = f"{BASE_URL}/fnlttSinglAcnt.json"
    p = {
        "crtfc_key": _key(),
        "corp_code": corp_code,
        "bsns_year": str(year),
        "reprt_code": reprt_code,
    }
    r = requests.get(url, params=p, timeout=30)
    r.raise_for_status()
    return r.json()
