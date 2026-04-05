#!/usr/bin/env python3
"""
collect_energy.py — 에너지 데이터 크롤러
저장 테이블: energy
소스: EIA Open Data API

사용법:
    python collect_energy.py              # 최근 365일
    python collect_energy.py --days 90    # 최근 90일

EIA API key 등록 (무료):
    https://www.eia.gov/opendata/register.php
    export EIA_API_KEY='your_key_here'
"""

import argparse
import json
import sqlite3
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# load_env 는 같은 디렉터리
from load_env import get_key

DB_PATH = Path(__file__).resolve().parent.parent / 'db' / 'raw.db'

EIA_SERIES = {
    # 원유
    'PET.RWTC.D': {'category': 'crude_oil', 'unit': 'USD/barrel', 'name': 'WTI Spot'},
    'PET.RBRTE.D': {'category': 'crude_oil', 'unit': 'USD/barrel', 'name': 'Brent Spot'},
    'PET.WCESTUS1.W': {'category': 'crude_oil', 'unit': 'thousand barrels', 'name': 'US Crude Inventory'},

    # 천연가스
    'NG.RNGWHHD.D': {'category': 'natural_gas', 'unit': 'USD/MMBtu', 'name': 'Henry Hub Spot'},
    'NG.NW2_EPG0_SWO_R48_BCF.W': {'category': 'natural_gas', 'unit': 'BCF', 'name': 'US NG Storage'},

    # 전력
    'ELEC.PRICE.US-ALL.M': {'category': 'electricity', 'unit': 'cents/kWh', 'name': 'US Avg Electricity Price'},

    # 석탄
    'COAL.PRICE_BY_RANK.US-TOT.W': {'category': 'coal', 'unit': 'USD/short ton', 'name': 'US Coal Price'},
}


def _parse_series_id(series_id: str):
    """EIA series ID를 API v2 route와 facet으로 분해한다.

    EIA v2 URL 패턴:
        https://api.eia.gov/v2/{route}/data/?api_key=...&data[0]=value&...

    예시:
        PET.RWTC.D   → route='petroleum/pri/spt', series='RWTC', freq='daily'
        NG.RNGWHHD.D → route='natural-gas/pri/sum', series='RNGWHHD', freq='daily'

    EIA v2 API는 시리즈마다 경로가 다르므로,
    v1 호환 endpoint를 사용하여 안정적으로 조회한다.
    """
    # EIA v2에서는 v1 series-id를 그대로 쓸 수 있는 호환 경로가 존재
    return series_id


def fetch_eia_series(series_id: str, api_key: str, start_date: str) -> list:
    """EIA API v2에서 시계열 데이터를 조회한다.

    EIA v2는 route 기반이지만, 아래 패턴으로 series 조회가 가능하다:
        https://api.eia.gov/v2/seriesid/{SERIES_ID}?api_key=...&data[0]=value&start={date}

    Returns:
        [{'date': '2024-01-02', 'value': 72.5}, ...]
    """
    # EIA v2 호환 endpoint
    encoded_id = urllib.request.quote(series_id, safe='')
    url = (
        f"https://api.eia.gov/v2/seriesid/{encoded_id}"
        f"?api_key={api_key}"
        f"&data[0]=value"
        f"&start={start_date}"
        f"&sort[0][column]=period"
        f"&sort[0][direction]=asc"
        f"&length=5000"
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

    # v2 response: { "response": { "data": [ {"period": "2024-01", "value": 72.5}, ... ] } }
    response = data.get('response', {})
    rows = response.get('data', [])

    records = []
    for row in rows:
        period = row.get('period')
        val = row.get('value')
        if period is None or val is None:
            continue
        try:
            records.append({
                'date': str(period),
                'value': float(val),
            })
        except (ValueError, TypeError):
            continue

    return records


def save_to_db(records: list) -> int:
    """energy 테이블에 INSERT OR REPLACE.

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
        INSERT OR REPLACE INTO energy
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
    parser = argparse.ArgumentParser(description='EIA Open Data API crawler for energy table')
    parser.add_argument('--days', type=int, default=365,
                        help='Number of days to look back (default: 365)')
    args = parser.parse_args()

    # API key check
    api_key = get_key('EIA_API_KEY')
    if not api_key:
        print("EIA API 키 미발급 — 건너뜀")
        return

    start_date = (datetime.now() - timedelta(days=args.days)).strftime('%Y-%m-%d')
    collected_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"=== EIA Energy Crawler ===")
    print(f"  Period : {start_date} ~ today")
    print(f"  Series : {len(EIA_SERIES)}")
    print(f"  DB     : {DB_PATH}")
    print()

    total_records = 0
    success_count = 0

    for i, (series_id, meta) in enumerate(EIA_SERIES.items(), 1):
        observations = fetch_eia_series(series_id, api_key, start_date)

        if observations:
            db_records = [
                {
                    'indicator_id': series_id,
                    'date': obs['date'],
                    'value': obs['value'],
                    'unit': meta['unit'],
                    'category': meta['category'],
                    'source': 'EIA',
                    'collected_at': collected_at,
                }
                for obs in observations
            ]
            save_to_db(db_records)
            total_records += len(db_records)
            success_count += 1
            print(f"  [{i:2d}/{len(EIA_SERIES)}] {meta['name']:30s} — {len(db_records):>4d} records")
        else:
            print(f"  [{i:2d}/{len(EIA_SERIES)}] {meta['name']:30s} — skip (no data)")

        # Rate limit
        time.sleep(0.3)

    print()
    print(f"=== Done: {success_count}/{len(EIA_SERIES)} series, {total_records} total records ===")


if __name__ == '__main__':
    main()
