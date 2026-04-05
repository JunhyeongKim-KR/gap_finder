#!/usr/bin/env python3
"""한국은행 ECOS API 크롤러 — raw.db macro_indicators 테이블에 저장.

ECOS Open API: https://ecos.bok.or.kr/api/
표준 라이브러리만 사용 (urllib, json, sqlite3).
"""

import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "raw.db"

ECOS_API_KEY = os.environ.get("ECOS_API_KEY", "YOUR_API_KEY_HERE")
ECOS_BASE_URL = "https://ecos.bok.or.kr/api/StatisticSearch"

# {통계표코드}/{항목코드} → 메타 정보
ECOS_SERIES = {
    # 금리
    "722Y001/0101000":    {"category": "interest_rate", "unit": "%",     "name": "기준금리"},
    "817Y002/010200000":  {"category": "interest_rate", "unit": "%",     "name": "국고채 3년"},
    "817Y002/010210000":  {"category": "interest_rate", "unit": "%",     "name": "국고채 10년"},
    # 환율
    "731Y003/0000001":    {"category": "exchange_rate", "unit": "KRW",   "name": "원/달러"},
    "731Y003/0000053":    {"category": "exchange_rate", "unit": "KRW",   "name": "원/엔(100엔)"},
    # 물가
    "901Y009/0":          {"category": "inflation",     "unit": "index", "name": "소비자물가지수"},
    "901Y010/0":          {"category": "inflation",     "unit": "index", "name": "생산자물가지수"},
    # 통화
    "101Y003/BBFA00":     {"category": "liquidity",     "unit": "십억원", "name": "M2"},
}

# 주기 매핑: 금리/환율은 일별(D), 물가/통화는 월별(M)
FREQ_MAP = {
    "interest_rate": "D",
    "exchange_rate":  "D",
    "inflation":      "M",
    "liquidity":      "M",
}


def build_url(stat_code: str, item_code: str, freq: str,
              start_date: str, end_date: str,
              start_idx: int = 1, end_idx: int = 1000) -> str:
    """ECOS StatisticSearch API URL을 조립한다."""
    # URL 형식: /api/StatisticSearch/{API_KEY}/json/kr/{start}/{end}/{stat_code}/{freq}/{start_date}/{end_date}/{item_code}
    return (
        f"{ECOS_BASE_URL}/{ECOS_API_KEY}/json/kr"
        f"/{start_idx}/{end_idx}"
        f"/{stat_code}/{freq}/{start_date}/{end_date}/{item_code}"
    )


def fetch_series(stat_code: str, item_code: str, meta: dict,
                 start_date: str, end_date: str) -> list:
    """단일 시리즈 데이터를 가져온다."""
    freq = FREQ_MAP.get(meta["category"], "M")
    url = build_url(stat_code, item_code, freq, start_date, end_date)

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"    HTTP 오류 {e.code}: {e.reason}")
        return []
    except urllib.error.URLError as e:
        print(f"    연결 오류: {e.reason}")
        return []
    except Exception as e:
        print(f"    요청 오류: {e}")
        return []

    # ECOS 에러 응답 처리
    if "StatisticSearch" not in data:
        err = data.get("RESULT", {})
        print(f"    API 에러: {err.get('CODE', '?')} — {err.get('MESSAGE', '알 수 없음')}")
        return []

    rows = data["StatisticSearch"].get("row", [])
    results = []
    for row in rows:
        raw_time = row.get("TIME", "")
        value_str = row.get("DATA_VALUE", "")

        # 날짜 정규화: YYYYMMDD → YYYY-MM-DD, YYYYMM → YYYY-MM-01
        if len(raw_time) == 8:
            date_str = f"{raw_time[:4]}-{raw_time[4:6]}-{raw_time[6:8]}"
        elif len(raw_time) == 6:
            date_str = f"{raw_time[:4]}-{raw_time[4:6]}-01"
        elif len(raw_time) == 4:
            date_str = f"{raw_time}-01-01"
        else:
            date_str = raw_time

        try:
            value = float(value_str)
        except (ValueError, TypeError):
            continue

        results.append({"date": date_str, "value": value})

    return results


def save_to_db(conn: sqlite3.Connection, indicator_id: str, meta: dict, rows: list):
    """macro_indicators 테이블에 저장한다."""
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    count = 0

    for r in rows:
        cur.execute("""
        INSERT OR REPLACE INTO macro_indicators
            (indicator_id, date, value, unit, category, source, collected_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            indicator_id, r["date"], r["value"],
            meta["unit"], meta["category"], "ECOS", now,
        ))
        count += 1

    conn.commit()
    return count


def main():
    # API 키 확인
    if ECOS_API_KEY == "YOUR_API_KEY_HERE":
        print("[경고] ECOS_API_KEY가 설정되지 않았습니다.")
        print("  export ECOS_API_KEY='발급받은키' 로 설정 후 다시 실행하세요.")
        print("  키 발급: https://ecos.bok.or.kr/api/#/AuthKeyApply")
        print()

    # 기간 설정
    end_date = datetime.now().strftime("%Y%m%d")
    # 기본 3년 수집; 인자로 시작날짜 지정 가능 (YYYYMMDD)
    if len(sys.argv) > 1:
        start_date = sys.argv[1]
    else:
        start_date = str(int(end_date[:4]) - 3) + end_date[4:]

    print(f"=== ECOS 매크로 지표 수집 ===")
    print(f"기간: {start_date} ~ {end_date}")
    print(f"DB  : {DB_PATH}\n")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")

    total_saved = 0
    success_count = 0

    for series_key, meta in ECOS_SERIES.items():
        stat_code, item_code = series_key.split("/")
        indicator_id = f"ECOS:{stat_code}:{item_code}"

        print(f"  [{meta['name']}] 수집 중... ({stat_code}/{item_code})")

        rows = fetch_series(stat_code, item_code, meta, start_date, end_date)

        if rows:
            saved = save_to_db(conn, indicator_id, meta, rows)
            total_saved += saved
            success_count += 1
            print(f"    → {saved}건 저장")
        else:
            print(f"    → 데이터 없음")

        # Rate limit: 요청 간 0.5초 대기
        time.sleep(0.5)

    conn.close()

    print(f"\n=== 수집 완료 ===")
    print(f"  성공: {success_count}/{len(ECOS_SERIES)} 시리즈")
    print(f"  총 {total_saved}건 저장")


if __name__ == "__main__":
    main()
