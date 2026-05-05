"""매주 월요일 후보 15개 자동 산출.

universe(KOSPI200 + KOSDAQ150 + S&P500 ≈ 850종목)에서 5개 trigger 필터:
1. 최근 7일 내 증권사 추정치 변경
2. 최근 7일 내 가격 ±10% 이상 변동
3. 최근 분기 EPS surprise ±20%
4. 최근 7일 내 뉴스 빈도 평균 ±2σ
5. 최근 분기 RPO·deferred revenue·재고 등 재무 이상치 (5년 평균 ±2σ)

→ 글 가치 필터 (네이버 검색량 + Google Trends 합 상위 80%)
→ 상위 15개 출력 (종목명 + trigger 종류 + 1줄 요약)

Phase A skeleton — 실제 데이터 호출은 Phase C 이후.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def build_universe() -> list[str]:
    """KOSPI200 + KOSDAQ150 + S&P500 — Phase C에서 실제 구현."""
    raise NotImplementedError("universe 구성은 Phase C")


def apply_triggers(universe: list[str]) -> list[dict]:
    """5개 trigger 필터 — Phase C에서 실제 구현."""
    raise NotImplementedError("trigger 필터는 Phase C")


def filter_search_demand(candidates: list[dict]) -> list[dict]:
    """네이버 검색량 + Google Trends 상위 80% — Phase C."""
    raise NotImplementedError("검색량 필터는 Phase C")


def main() -> None:
    parser = argparse.ArgumentParser(description="주간 longlist 생성")
    parser.add_argument("--top", type=int, default=15)
    args = parser.parse_args()

    today = dt.date.today()
    print(f"[skeleton] longlist {today.isoformat()} top={args.top}")

    out = DATA_DIR / "candidates" / f"longlist_{today.isoformat()}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps({"date": today.isoformat(), "candidates": [], "status": "skeleton"}, indent=2),
        encoding="utf-8",
    )
    print(f"[skeleton] wrote {out}")


if __name__ == "__main__":
    main()
