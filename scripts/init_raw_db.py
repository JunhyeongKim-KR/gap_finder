#!/usr/bin/env python3
"""GapFinder raw.db 초기화 스크립트.

raw.db는 크롤링으로 수집한 가공 전 원본 데이터만 저장한다.
투자 판단, 프레임워크, 해석 등은 포함하지 않는다.
enriched.db에서 raw.db를 참조하여 재해석한다.

2-DB 아키텍처:
  - raw.db      : 크롤링 원본 (이 스크립트)
  - enriched.db : 해석/분석 결과
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "raw.db"

TABLES_SQL = [
    # 1. 종목 기본정보 (크롤링으로 수집)
    """
    CREATE TABLE IF NOT EXISTS stock_info (
        ticker          TEXT PRIMARY KEY,
        name_kr         TEXT,
        name_en         TEXT,
        market          TEXT CHECK(market IN ('KR_KOSPI','KR_KOSDAQ','US_NYSE','US_NASDAQ')),
        sector          TEXT,
        sub_sector      TEXT,
        market_cap      REAL,
        market_cap_date TEXT,
        collected_at    TEXT DEFAULT (datetime('now'))
    )
    """,

    # 2. 분기별 재무 (OpenDART, SEC EDGAR, yfinance)
    """
    CREATE TABLE IF NOT EXISTS financials (
        ticker           TEXT,
        fiscal_period    TEXT,
        revenue          REAL,
        operating_income REAL,
        net_income       REAL,
        ebitda           REAL,
        eps              REAL,
        bps              REAL,
        roe              REAL,
        debt_ratio       REAL,
        ocf              REAL,
        fcf              REAL,
        capex            REAL,
        per              REAL,
        pbr              REAL,
        ev_ebitda        REAL,
        source           TEXT,
        collected_at     TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (ticker, fiscal_period)
    )
    """,

    # 3. 일별 시세 (KRX, yfinance)
    """
    CREATE TABLE IF NOT EXISTS price_daily (
        ticker      TEXT,
        date        TEXT,
        open        REAL,
        high        REAL,
        low         REAL,
        close       REAL,
        volume      INTEGER,
        market_cap  REAL,
        source      TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (ticker, date)
    )
    """,

    # 4. 매크로 지표 (FRED, ECOS, EIA, BLS)
    """
    CREATE TABLE IF NOT EXISTS macro_indicators (
        indicator_id TEXT,
        date         TEXT,
        value        REAL,
        unit         TEXT,
        category     TEXT CHECK(category IN (
            'interest_rate','exchange_rate','commodity','inflation',
            'employment','gdp','energy','trade','credit_spread','liquidity'
        )),
        source       TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (indicator_id, date)
    )
    """,

    # 5. 뉴스 (Google News RSS, 공식 보도자료)
    """
    CREATE TABLE IF NOT EXISTS news (
        news_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker       TEXT,
        title        TEXT,
        url          TEXT,
        source       TEXT,
        published_at TEXT,
        summary      TEXT,
        sentiment    TEXT,
        collected_at TEXT DEFAULT (datetime('now'))
    )
    """,

    # 6. 공시 (OpenDART, SEC EDGAR)
    """
    CREATE TABLE IF NOT EXISTS filings (
        filing_id    TEXT PRIMARY KEY,
        ticker       TEXT,
        filing_type  TEXT,
        title        TEXT,
        url          TEXT,
        filed_at     TEXT,
        source       TEXT CHECK(source IN ('DART','SEC_EDGAR','KIND')),
        collected_at TEXT DEFAULT (datetime('now'))
    )
    """,

    # 7. 컨센서스 (네이버증권, FnGuide)
    """
    CREATE TABLE IF NOT EXISTS consensus (
        ticker            TEXT,
        date              TEXT,
        analyst_count     INTEGER,
        buy_count         INTEGER,
        hold_count        INTEGER,
        sell_count        INTEGER,
        target_price_avg  REAL,
        target_price_high REAL,
        target_price_low  REAL,
        eps_estimate      REAL,
        revenue_estimate  REAL,
        source            TEXT,
        collected_at      TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (ticker, date)
    )
    """,

    # 8. 무역 통계 (관세청, Census)
    """
    CREATE TABLE IF NOT EXISTS trade_stats (
        country          TEXT,
        date             TEXT,
        export_value     REAL,
        import_value     REAL,
        trade_balance    REAL,
        product_category TEXT,
        source           TEXT,
        collected_at     TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (country, date, product_category)
    )
    """,

    # 9. 에너지 데이터 (EIA)
    """
    CREATE TABLE IF NOT EXISTS energy (
        indicator_id TEXT,
        date         TEXT,
        value        REAL,
        unit         TEXT,
        category     TEXT CHECK(category IN (
            'crude_oil','natural_gas','electricity','coal','nuclear','renewable'
        )),
        source       TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (indicator_id, date)
    )
    """,
]


def create_tables(conn: sqlite3.Connection) -> None:
    """모든 테이블을 생성한다."""
    cur = conn.cursor()
    for sql in TABLES_SQL:
        cur.execute(sql)
    conn.commit()


def print_summary(conn: sqlite3.Connection) -> None:
    """생성된 테이블 이름과 컬럼 수를 출력한다."""
    cur = conn.cursor()
    tables = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    print(f"\n{'테이블':<22} {'컬럼 수':>6}")
    print("-" * 30)
    for (table_name,) in tables:
        cols = cur.execute(f"PRAGMA table_info({table_name})").fetchall()
        print(f"  {table_name:<20} {len(cols):>4}")
    print("-" * 30)
    print(f"  총 {len(tables)}개 테이블 생성 완료\n")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"[raw.db] 경로: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")

    print("[raw.db] 테이블 생성 중...")
    create_tables(conn)
    print_summary(conn)

    conn.close()
    print("[raw.db] 초기화 완료!")


if __name__ == "__main__":
    main()
