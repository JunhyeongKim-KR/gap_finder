#!/usr/bin/env python3
"""매크로 지표 수집 — yfinance 기반 (API 키 불필요).

주요 지수/원자재/금리 ETF를 통해 매크로 데이터를 수집한다.
FRED API 키가 있으면 추후 직접 연동 가능.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

import yfinance as yf

RAW_DIR = Path(__file__).resolve().parent.parent / "raw" / "macro"

# 매크로 프록시 티커 목록
MACRO_TICKERS = {
    # 주요 지수
    "^GSPC":     {"name": "S&P 500",           "category": "지수"},
    "^IXIC":     {"name": "NASDAQ Composite",   "category": "지수"},
    "^KS11":     {"name": "KOSPI",              "category": "지수"},
    "^KQ11":     {"name": "KOSDAQ",             "category": "지수"},

    # 금리 (국채 ETF → 금리 역방향 프록시)
    "^TNX":      {"name": "미국 10년 국채금리",   "category": "금리"},
    "^FVX":      {"name": "미국 5년 국채금리",    "category": "금리"},
    "^IRX":      {"name": "미국 3개월 국채금리",  "category": "금리"},

    # 환율
    "KRW=X":     {"name": "USD/KRW 환율",       "category": "환율"},
    "JPY=X":     {"name": "USD/JPY 환율",       "category": "환율"},
    "DX-Y.NYB":  {"name": "달러 인덱스(DXY)",   "category": "환율"},

    # 원자재
    "CL=F":      {"name": "WTI 원유",           "category": "원자재"},
    "GC=F":      {"name": "금",                 "category": "원자재"},
    "HG=F":      {"name": "구리",               "category": "원자재"},

    # 변동성
    "^VIX":      {"name": "VIX (변동성지수)",    "category": "센티먼트"},
}


def collect_macro(period: str = "3mo") -> dict:
    """매크로 지표 일괄 수집."""
    print(f"매크로 지표 수집 중 (기간: {period})...\n")

    results = {}
    for ticker, meta in MACRO_TICKERS.items():
        try:
            data = yf.Ticker(ticker)
            hist = data.history(period=period)

            if hist.empty:
                print(f"  [{meta['name']}] 데이터 없음 — 스킵")
                continue

            latest = hist.iloc[-1]
            prev = hist.iloc[-2] if len(hist) > 1 else latest
            first = hist.iloc[0]

            change_1d = ((latest["Close"] - prev["Close"]) / prev["Close"]) * 100
            change_period = ((latest["Close"] - first["Close"]) / first["Close"]) * 100

            results[ticker] = {
                "name": meta["name"],
                "category": meta["category"],
                "latest_date": hist.index[-1].strftime("%Y-%m-%d"),
                "latest_close": round(latest["Close"], 4),
                "prev_close": round(prev["Close"], 4),
                "change_1d_pct": round(change_1d, 2),
                "change_period_pct": round(change_period, 2),
                "period_high": round(hist["High"].max(), 4),
                "period_low": round(hist["Low"].min(), 4),
            }
            print(f"  {meta['name']:20s} | {results[ticker]['latest_close']:>12,.2f} | 1일 {change_1d:+.2f}% | {period} {change_period:+.2f}%")

        except Exception as e:
            print(f"  [{meta['name']}] 오류: {e}")

    return results


def save_raw(results: dict):
    """raw/macro/에 JSON으로 저장."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M")
    path = RAW_DIR / f"macro_snapshot_{now}.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump({"collected_at": now, "indicators": results},
                  f, ensure_ascii=False, indent=2)

    print(f"\n저장 → {path}")


def print_summary(results: dict):
    """카테고리별 요약."""
    print(f"\n{'='*60}")
    categories = {}
    for ticker, data in results.items():
        cat = data["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(data)

    for cat, items in categories.items():
        print(f"\n  [{cat}]")
        for item in items:
            arrow = "▲" if item["change_1d_pct"] > 0 else "▼" if item["change_1d_pct"] < 0 else "─"
            print(f"    {item['name']:20s} {item['latest_close']:>12,.2f}  {arrow} {item['change_1d_pct']:+.2f}%")


def main():
    period = sys.argv[1] if len(sys.argv) > 1 else "3mo"
    print(f"=== 매크로 지표 수집 (yfinance) ===\n")

    results = collect_macro(period)
    save_raw(results)
    print_summary(results)

    print(f"\n=== 수집 완료 ({len(results)}/{len(MACRO_TICKERS)} 지표) ===")


if __name__ == "__main__":
    main()
