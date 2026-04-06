#!/usr/bin/env python3
"""
raw.db 초기화 — 1층 원문 저장 + 2층 정형 데이터

CEO 3층 구조: 원문/정형/해석 중 1~2층 담당
  - 1층: 원문 저장 (documents)
  - 2층: 정형 데이터 (companies, financials, price_daily, ...)
  - 3층: 해석 → enriched.db (별도)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "raw.db"

# Layer assignment for summary output
LAYER_1_TABLES = ["documents"]
LAYER_2_TABLES = [
    "companies", "financials", "price_daily", "macro_indicators",
    "industry_metrics", "events", "consensus", "trade_stats", "energy",
]

TABLES = {

    # ===== 1층: 원문 저장 =====

    "documents": """
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        title TEXT,
        source TEXT,
        source_type TEXT CHECK(source_type IN (
            'news','report','filing','blog','policy',
            'ir_transcript','press_release','regulation'
        )),
        published_at TEXT,
        url TEXT,
        raw_text TEXT,
        cleaned_text TEXT,
        language TEXT CHECK(language IN ('ko','en','other')),
        tags TEXT,
        related_tickers TEXT,
        collected_at TEXT DEFAULT (datetime('now'))
    )""",

    # ===== 2층: 정형 데이터 =====

    "companies": """
    CREATE TABLE IF NOT EXISTS companies (
        ticker TEXT PRIMARY KEY,
        name_kr TEXT,
        name_en TEXT,
        market TEXT CHECK(market IN (
            'KR_KOSPI','KR_KOSDAQ','US_NYSE','US_NASDAQ'
        )),
        country TEXT,
        sector TEXT,
        industry TEXT,
        sub_sector TEXT,
        description TEXT,
        market_cap REAL,
        market_cap_date TEXT,
        collected_at TEXT DEFAULT (datetime('now'))
    )""",

    "financials": """
    CREATE TABLE IF NOT EXISTS financials (
        ticker TEXT,
        fiscal_period TEXT,
        revenue REAL,
        operating_income REAL,
        net_income REAL,
        ebitda REAL,
        fcf REAL,
        capex REAL,
        cash REAL,
        debt REAL,
        shares_outstanding REAL,
        eps REAL,
        bps REAL,
        roe REAL,
        roic REAL,
        wacc REAL,
        reinvestment_rate REAL,
        debt_ratio REAL,
        ocf REAL,
        per REAL,
        pbr REAL,
        ev_ebitda REAL,
        p_fcf REAL,
        fcf_yield REAL,
        dividend REAL,
        buyback REAL,
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (ticker, fiscal_period)
    )""",

    "price_daily": """
    CREATE TABLE IF NOT EXISTS price_daily (
        ticker TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        market_cap REAL,
        per REAL,
        pbr REAL,
        ev_ebitda REAL,
        p_fcf REAL,
        fcf_yield REAL,
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (ticker, date)
    )""",

    "macro_indicators": """
    CREATE TABLE IF NOT EXISTS macro_indicators (
        indicator_id TEXT,
        date TEXT,
        value REAL,
        unit TEXT,
        country TEXT DEFAULT 'US',
        category TEXT CHECK(category IN (
            'interest_rate','exchange_rate','commodity',
            'inflation','employment','gdp','energy',
            'trade','credit_spread','liquidity'
        )),
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (indicator_id, date)
    )""",

    "industry_metrics": """
    CREATE TABLE IF NOT EXISTS industry_metrics (
        industry TEXT,
        date TEXT,
        capex REAL,
        depreciation REAL,
        capex_da_ratio REAL,
        ipo_count INTEGER,
        ma_count INTEGER,
        new_entrants INTEGER,
        avg_margin REAL,
        utilization_rate REAL,
        inventory_level REAL,
        supply_expansion_plan TEXT,
        price_competition TEXT CHECK(price_competition IN ('HIGH','MEDIUM','LOW')),
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (industry, date)
    )""",

    "events": """
    CREATE TABLE IF NOT EXISTS events (
        event_id TEXT PRIMARY KEY,
        event_type TEXT CHECK(event_type IN (
            'earnings','filing','ipo','ma','buyback',
            'dividend','capital_raise','policy','tariff',
            'regulation','conflict','sanction','macro',
            'product_launch','management_change','other'
        )),
        date TEXT,
        title TEXT,
        summary TEXT,
        url TEXT,
        source TEXT,
        source_doc_id TEXT,
        related_tickers TEXT,
        related_countries TEXT,
        related_industries TEXT,
        importance TEXT CHECK(importance IN ('HIGH','MEDIUM','LOW')),
        tags TEXT,
        collected_at TEXT DEFAULT (datetime('now'))
    )""",

    "consensus": """
    CREATE TABLE IF NOT EXISTS consensus (
        ticker TEXT,
        date TEXT,
        analyst_count INTEGER,
        buy_count INTEGER,
        hold_count INTEGER,
        sell_count INTEGER,
        target_price_avg REAL,
        target_price_high REAL,
        target_price_low REAL,
        eps_estimate REAL,
        revenue_estimate REAL,
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (ticker, date)
    )""",

    "trade_stats": """
    CREATE TABLE IF NOT EXISTS trade_stats (
        country TEXT,
        date TEXT,
        export_value REAL,
        import_value REAL,
        trade_balance REAL,
        product_category TEXT,
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (country, date, product_category)
    )""",

    "energy": """
    CREATE TABLE IF NOT EXISTS energy (
        indicator_id TEXT,
        date TEXT,
        value REAL,
        unit TEXT,
        category TEXT CHECK(category IN (
            'crude_oil','natural_gas','electricity',
            'coal','nuclear','renewable'
        )),
        source TEXT,
        collected_at TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (indicator_id, date)
    )""",
}


def create_tables(conn: sqlite3.Connection) -> None:
    """모든 테이블을 생성한다."""
    cur = conn.cursor()
    for sql in TABLES.values():
        cur.execute(sql)
    conn.commit()


def count_columns(conn: sqlite3.Connection, table_name: str) -> int:
    """테이블의 컬럼 수를 반환한다."""
    cols = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return len(cols)


def print_summary(conn: sqlite3.Connection) -> None:
    """생성된 테이블을 층별로 그룹핑하여 출력한다."""

    print(f"\n{'='*40}")
    print("=== 1층: 원문 저장 ===")
    print(f"{'='*40}")
    print(f"  {'테이블':<22} {'컬럼 수':>6}")
    print(f"  {'-'*28}")
    layer1_count = 0
    for name in LAYER_1_TABLES:
        ncols = count_columns(conn, name)
        print(f"  {name:<22} {ncols:>4}")
        layer1_count += 1

    print(f"\n{'='*40}")
    print("=== 2층: 정형 데이터 ===")
    print(f"{'='*40}")
    print(f"  {'테이블':<22} {'컬럼 수':>6}")
    print(f"  {'-'*28}")
    layer2_count = 0
    for name in LAYER_2_TABLES:
        ncols = count_columns(conn, name)
        print(f"  {name:<22} {ncols:>4}")
        layer2_count += 1

    total = layer1_count + layer2_count
    print(f"\n  {'-'*28}")
    print(f"  1층: {layer1_count}개 / 2층: {layer2_count}개 / 총 {total}개 테이블 생성 완료\n")


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
