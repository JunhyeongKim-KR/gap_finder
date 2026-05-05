"""Alpha Vantage — 시세·재무·외환·암호.

Endpoint: https://www.alphavantage.co/query
Doc: https://www.alphavantage.co/documentation/

Phase A skeleton. (free tier rate limit: 5 calls/min, 500/day)
"""
from __future__ import annotations

import os

import requests

BASE_URL = "https://www.alphavantage.co/query"


def _key() -> str:
    k = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    if not k:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY 가 .env 에 설정되지 않음")
    return k


def call(function: str, **params: object) -> dict:
    """함수형 호출. 예: function='OVERVIEW', symbol='ORCL'."""
    p = {"function": function, "apikey": _key(), **params}
    r = requests.get(BASE_URL, params=p, timeout=30)
    r.raise_for_status()
    return r.json()


def overview(symbol: str) -> dict:
    return call("OVERVIEW", symbol=symbol)


def income_statement(symbol: str) -> dict:
    return call("INCOME_STATEMENT", symbol=symbol)


def balance_sheet(symbol: str) -> dict:
    return call("BALANCE_SHEET", symbol=symbol)


def cash_flow(symbol: str) -> dict:
    return call("CASH_FLOW", symbol=symbol)


def earnings(symbol: str) -> dict:
    return call("EARNINGS", symbol=symbol)
