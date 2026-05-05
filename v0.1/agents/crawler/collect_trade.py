#!/usr/bin/env python3
"""
collect_trade.py — 무역 통계 크롤러
저장 테이블: trade_stats
소스: 관세청 무역통계 API (data.go.kr)

사용법:
    python collect_trade.py                          # 최근 365일, 기본 국가
    python collect_trade.py --days 90                # 최근 90일
    python collect_trade.py --countries US CN JP      # 특정 국가만

API key 등록:
    https://www.data.go.kr/ 에서 '수출입무역통계' 활용신청
    export DATA_GO_KR_API_KEY='your_key_here'
"""

import argparse
import json
import sqlite3
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path

from load_env import get_key

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / 'raw.db'

# 기본 대상 국가 코드 (관세청 2자리 코드)
DEFAULT_COUNTRIES = ['US', 'CN', 'JP', 'EU']

# 관세청 국가코드 → 표시명
COUNTRY_NAMES = {
    'US': '미국',
    'CN': '중국',
    'JP': '일본',
    'EU': '유럽연합',
    'DE': '독일',
    'VN': '베트남',
    'KR': '한국',
}

BASE_URL = 'http://apis.data.go.kr/1220000/retrieveExportImport/retrieveExportImport'


def fetch_trade_data(api_key: str, country: str, start_date: str, end_date: str) -> list:
    """관세청 무역통계 API에서 수출입 실적을 조회한다.

    Parameters:
        api_key: data.go.kr 서비스키
        country: 국가코드 (US, CN, JP, ...)
        start_date: 조회 시작일 (YYYYMMDD)
        end_date: 조회 종료일 (YYYYMMDD)

    Returns:
        [{'date': '202401', 'export_value': ..., 'import_value': ...}, ...]
    """
    params = {
        'serviceKey': api_key,
        'searchBgnDe': start_date,
        'searchEndDe': end_date,
        'cntyCd': country,
        'numOfRows': '1000',
        'pageNo': '1',
        'resultType': 'json',
    }

    url = BASE_URL + '?' + urllib.parse.urlencode(params, safe='=+/')

    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'GapFinder/1.0'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode('utf-8')
    except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
        print(f"    [ERROR] {country}: network error — {e}")
        return []

    # 응답 파싱 시도 (JSON)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # XML 응답인 경우 (에러 또는 구형 응답)
        try:
            root = ET.fromstring(raw)
            # 에러 메시지 확인
            err_msg = root.findtext('.//returnAuthMsg') or root.findtext('.//errMsg')
            if err_msg:
                print(f"    [ERROR] {country}: API error — {err_msg}")
            else:
                print(f"    [ERROR] {country}: unexpected XML response")
            return []
        except ET.ParseError:
            print(f"    [ERROR] {country}: cannot parse response")
            return []

    # JSON 구조 파싱
    # data.go.kr 표준 응답: { "response": { "header": {...}, "body": { "items": { "item": [...] } } } }
    records = []

    try:
        body = data.get('response', {}).get('body', {})
        items = body.get('items', {})

        # items가 빈 문자열이거나 None인 경우
        if not items:
            return []

        item_list = items.get('item', [])
        if isinstance(item_list, dict):
            item_list = [item_list]

        for item in item_list:
            # 관세청 필드명은 API 버전에 따라 다를 수 있음
            # 일반적: balPayDe(기간), expDlr(수출금액), impDlr(수입금액)
            period = item.get('balPayDe') or item.get('trdDe') or item.get('date', '')
            exp_val = item.get('expDlr') or item.get('expCnt') or 0
            imp_val = item.get('impDlr') or item.get('impCnt') or 0

            if not period:
                continue

            try:
                export_v = float(exp_val) if exp_val else 0.0
                import_v = float(imp_val) if imp_val else 0.0
            except (ValueError, TypeError):
                export_v = 0.0
                import_v = 0.0

            records.append({
                'date': str(period),
                'export_value': export_v,
                'import_value': import_v,
                'trade_balance': export_v - import_v,
            })

    except (AttributeError, TypeError, KeyError) as e:
        print(f"    [ERROR] {country}: response parsing error — {e}")
        return []

    return records


def save_to_db(records: list) -> int:
    """trade_stats 테이블에 INSERT OR REPLACE.

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
        INSERT OR REPLACE INTO trade_stats
            (country, date, export_value, import_value, trade_balance,
             product_category, source, collected_at)
        VALUES
            (:country, :date, :export_value, :import_value, :trade_balance,
             :product_category, :source, :collected_at)
        """,
        records,
    )
    conn.commit()
    count = cur.rowcount
    conn.close()
    return count


def main():
    parser = argparse.ArgumentParser(description='관세청 무역통계 API crawler for trade_stats')
    parser.add_argument('--days', type=int, default=365,
                        help='Number of days to look back (default: 365)')
    parser.add_argument('--countries', nargs='+', default=DEFAULT_COUNTRIES,
                        help=f'Country codes to query (default: {DEFAULT_COUNTRIES})')
    args = parser.parse_args()

    # API key check
    api_key = get_key('DATA_GO_KR_API_KEY')
    if not api_key:
        print("관세청 API 키 미발급 — 건너뜀")
        return

    end_dt = datetime.now()
    start_dt = end_dt - timedelta(days=args.days)
    start_date = start_dt.strftime('%Y%m%d')
    end_date = end_dt.strftime('%Y%m%d')
    collected_at = end_dt.strftime('%Y-%m-%d %H:%M:%S')

    countries = [c.upper() for c in args.countries]

    print(f"=== 관세청 무역통계 Crawler ===")
    print(f"  Period    : {start_date} ~ {end_date}")
    print(f"  Countries : {countries}")
    print(f"  DB        : {DB_PATH}")
    print()

    total_records = 0
    success_count = 0

    for i, country in enumerate(countries, 1):
        country_name = COUNTRY_NAMES.get(country, country)
        observations = fetch_trade_data(api_key, country, start_date, end_date)

        if observations:
            db_records = [
                {
                    'country': country,
                    'date': obs['date'],
                    'export_value': obs['export_value'],
                    'import_value': obs['import_value'],
                    'trade_balance': obs['trade_balance'],
                    'product_category': 'total',
                    'source': 'CUSTOMS_KR',
                    'collected_at': collected_at,
                }
                for obs in observations
            ]
            save_to_db(db_records)
            total_records += len(db_records)
            success_count += 1
            print(f"  [{i:2d}/{len(countries)}] {country_name:20s} ({country}) — {len(db_records):>4d} records")
        else:
            print(f"  [{i:2d}/{len(countries)}] {country_name:20s} ({country}) — skip (no data)")

        # Rate limit
        time.sleep(0.5)

    print()
    print(f"=== Done: {success_count}/{len(countries)} countries, {total_records} total records ===")


if __name__ == '__main__':
    main()
