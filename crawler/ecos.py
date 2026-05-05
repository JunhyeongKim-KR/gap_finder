"""ECOS — 한국은행 경제통계시스템.

Endpoint: https://ecos.bok.or.kr/api/
Doc: https://ecos.bok.or.kr/api/#/AddInfo/GuideInfo

Phase A skeleton.
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://ecos.bok.or.kr/api"


def _key() -> str:
    k = os.getenv("ECOS_API_KEY", "")
    if not k:
        raise RuntimeError("ECOS_API_KEY 가 .env 에 설정되지 않음")
    return k


def get_statistic_list(start: int = 1, end: int = 100) -> dict:
    """통계 목록 조회."""
    url = f"{BASE_URL}/StatisticTableList/{_key()}/json/kr/{start}/{end}"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()


def get_statistic_search(
    stat_code: str, cycle: str, start_date: str, end_date: str, item1: str = "", item2: str = ""
) -> dict:
    """통계 데이터 조회. cycle: A=년, Q=분기, M=월, D=일. start/end: YYYYMMDD."""
    url = (
        f"{BASE_URL}/StatisticSearch/{_key()}/json/kr/1/100/"
        f"{stat_code}/{cycle}/{start_date}/{end_date}/{item1}/{item2}"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return r.json()
