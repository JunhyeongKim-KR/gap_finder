#!/usr/bin/env python3
"""
FRED API 크롤러 — raw.db macro_indicators 테이블에 저장
1차 구축 소스: 금리, 환율, 원자재, 물가, 고용, 경기, 신용스프레드, 유동성

사용법:
    python collect_fred.py              # 최근 365일
    python collect_fred.py --days 90    # 최근 90일
    python collect_fred.py --days 3650  # 최근 10년

FRED API key 등록 (무료):
    https://fred.stlouisfed.org/docs/api/api_key.html
    export FRED_API_KEY='your_key_here'
"""

import argparse
import json
import os
import sqlite3
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

FRED_API_KEY = os.environ.get('FRED_API_KEY', 'YOUR_API_KEY_HERE')

DB_PATH = Path(__file__).resolve().parent.parent / 'db' / 'raw.db'

FRED_SERIES = {
    # 금리
    'DFF':    {'category': 'interest_rate', 'unit': '%',         'name': 'Federal Funds Rate'},
    'DGS2':   {'category': 'interest_rate', 'unit': '%',         'name': '2Y Treasury'},
    'DGS10':  {'category': 'interest_rate', 'unit': '%',         'name': '10Y Treasury'},
    'T10Y2Y': {'category': 'interest_rate', 'unit': '%',         'name': '10Y-2Y Spread'},
    'T10Y3M': {'category': 'interest_rate', 'unit': '%',         'name': '10Y-3M Spread'},

    # 환율
    'DEXKOUS':  {'category': 'exchange_rate', 'unit': 'KRW/USD', 'name': 'USD/KRW'},
    'DEXJPUS':  {'category': 'exchange_rate', 'unit': 'JPY/USD', 'name': 'USD/JPY'},
    'DEXUSEU':  {'category': 'exchange_rate', 'unit': 'USD/EUR', 'name': 'EUR/USD'},
    'DTWEXBGS': {'category': 'exchange_rate', 'unit': 'index',   'name': 'USD Index (Broad)'},

    # 원자재
    'DCOILWTICO':        {'category': 'commodity', 'unit': 'USD/barrel', 'name': 'WTI Crude Oil'},
    'DCOILBRENTEU':      {'category': 'commodity', 'unit': 'USD/barrel', 'name': 'Brent Crude'},
    'DHHNGSP':           {'category': 'commodity', 'unit': 'USD/MMBtu', 'name': 'Henry Hub Natural Gas'},
    'GOLDAMGBD228NLBM':  {'category': 'commodity', 'unit': 'USD/oz',    'name': 'Gold Price'},

    # 물가
    'CPIAUCSL': {'category': 'inflation', 'unit': 'index', 'name': 'CPI (All Urban)'},
    'CPILFESL': {'category': 'inflation', 'unit': 'index', 'name': 'Core CPI'},
    'PPIACO':   {'category': 'inflation', 'unit': 'index', 'name': 'PPI (All Commodities)'},
    'PCEPILFE': {'category': 'inflation', 'unit': 'index', 'name': 'Core PCE'},

    # 고용
    'UNRATE': {'category': 'employment', 'unit': '%',        'name': 'Unemployment Rate'},
    'PAYEMS': {'category': 'employment', 'unit': 'thousands', 'name': 'Nonfarm Payrolls'},
    'ICSA':   {'category': 'employment', 'unit': 'persons',   'name': 'Initial Jobless Claims'},

    # 경기
    'GDP':     {'category': 'gdp', 'unit': 'billions', 'name': 'US GDP'},
    'INDPRO':  {'category': 'gdp', 'unit': 'index',    'name': 'Industrial Production'},
    'UMCSENT': {'category': 'gdp', 'unit': 'index',    'name': 'Consumer Sentiment'},

    # 신용스프레드
    'BAMLH0A0HYM2': {'category': 'credit_spread', 'unit': '%', 'name': 'US HY OAS'},
    'BAMLC0A4CBBB':  {'category': 'credit_spread', 'unit': '%', 'name': 'BBB OAS'},

    # 유동성
    'WALCL': {'category': 'liquidity', 'unit': 'millions', 'name': 'Fed Balance Sheet'},
    'M2SL':  {'category': 'liquidity', 'unit': 'billions', 'name': 'M2 Money Supply'},
}


def fetch_fred_series(series_id: str, start_date: str) -> list[dict]:
    """FRED API에서 시계열 데이터를 조회한다.

    Returns:
        [{'date': '2024-01-02', 'value': 5.33}, ...]
        네트워크/파싱 오류 시 빈 리스트 반환.
    """
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}"
        f"&api_key={FRED_API_KEY}"
        f"&file_type=json"
        f"&observation_start={start_date}"
    )

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'GapFinder/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"    [ERROR] {series_id}: network error — {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"    [ERROR] {series_id}: JSON parse error — {e}")
        return []

    records = []
    for obs in data.get('observations', []):
        val_str = obs.get('value', '.')
        if val_str == '.':
            # FRED uses '.' for missing/unavailable values
            continue
        try:
            records.append({
                'date': obs['date'],
                'value': float(val_str),
            })
        except (ValueError, KeyError):
            continue

    return records


def save_to_db(records: list[dict]) -> int:
    """macro_indicators 테이블에 INSERT OR REPLACE.

    Returns:
        삽입/갱신된 레코드 수.
    """
    if not records:
        return 0

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    cur = conn.cursor()

    cur.executemany(
        """
        INSERT OR REPLACE INTO macro_indicators
            (indicator_id, date, value, unit, category, source, collected_at)
        VALUES
            (:indicator_id, :date, :value, :unit, :category, :source, :collected_at)
        """,
        records,
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def main():
    parser = argparse.ArgumentParser(description='FRED API crawler for macro_indicators')
    parser.add_argument('--days', type=int, default=365,
                        help='Number of days to look back (default: 365)')
    args = parser.parse_args()

    # API key check
    if FRED_API_KEY in ('YOUR_API_KEY_HERE', '', None):
        print("[WARNING] FRED_API_KEY is not set.")
        print("  export FRED_API_KEY='your_key_here'")
        print("  Register free at: https://fred.stlouisfed.org/docs/api/api_key.html")
        return

    start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
    collected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"=== FRED Crawler ===")
    print(f"  Period : {start_date} ~ today")
    print(f"  Series : {len(FRED_SERIES)}")
    print(f"  DB     : {DB_PATH}")
    print()

    total_records = 0
    success_count = 0

    for i, (series_id, meta) in enumerate(FRED_SERIES.items(), 1):
        observations = fetch_fred_series(series_id, start_date)

        if observations:
            db_records = [
                {
                    'indicator_id': series_id,
                    'date': obs['date'],
                    'value': obs['value'],
                    'unit': meta['unit'],
                    'category': meta['category'],
                    'source': 'FRED',
                    'collected_at': collected_at,
                }
                for obs in observations
            ]
            save_to_db(db_records)
            total_records += len(db_records)
            success_count += 1
            print(f"  [{i:2d}/{len(FRED_SERIES)}] {meta['name']:30s} — {len(db_records):>4d} records")
        else:
            print(f"  [{i:2d}/{len(FRED_SERIES)}] {meta['name']:30s} — skip (no data)")

        # Rate limit: max 5 req/sec
        time.sleep(0.2)

    print()
    print(f"=== Done: {success_count}/{len(FRED_SERIES)} series, {total_records} total records ===")


if __name__ == '__main__':
    main()
