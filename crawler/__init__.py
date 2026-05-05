"""GapFinder 외부 데이터 crawler 모듈.

각 모듈은 단일 외부 API에 대한 wrapper. Phase A는 skeleton — 실제 호출은 Phase C.

| 모듈              | 소스                | 용도                    | API key                |
|-------------------|---------------------|-------------------------|------------------------|
| fred              | FRED                | 미국 거시 통계          | FRED_API_KEY           |
| eia               | EIA                 | 미국 에너지 통계        | EIA_API_KEY            |
| ecos              | 한국은행 ECOS       | 한국 거시·통화          | ECOS_API_KEY           |
| bls               | US BLS              | 미국 노동 통계          | BLS_API_KEY            |
| dart              | 금감원 DART         | 한국 공시               | DART_API_KEY           |
| data_go_kr        | 공공데이터포털       | 한국 공공 데이터        | DATA_GO_KR_API_KEY     |
| finnhub           | Finnhub             | 글로벌 종목·뉴스·재무   | FINNHUB_API_KEY        |
| alpha_vantage     | Alpha Vantage       | 시세·재무               | ALPHA_VANTAGE_API_KEY  |
| polygon           | Polygon.io          | 미국 주식 시세          | POLYGON_API_KEY        |
| newsapi           | NewsAPI             | 글로벌 뉴스             | NEWSAPI_KEY            |
| naver             | Naver Search        | 한국 뉴스·검색          | NAVER_CLIENT_*         |
"""
from __future__ import annotations

__all__ = [
    "fred",
    "eia",
    "ecos",
    "bls",
    "dart",
    "data_go_kr",
    "finnhub",
    "alpha_vantage",
    "polygon",
    "newsapi",
    "naver",
]
