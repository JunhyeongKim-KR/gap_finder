#!/usr/bin/env python3
"""
enriched.db 초기화 — 3층 해석/지식 레이어
CEO 3층 구조: 원문/정형/해석 중 3층 담당
재해석 Agent가 raw.db를 읽고 철학 프레임을 적용하여 생성
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent.parent / "db" / "enriched.db"

# ===== 3층: 해석/지식 =====

TABLES = {

    'stock_analysis': """
CREATE TABLE IF NOT EXISTS stock_analysis (
    ticker TEXT PRIMARY KEY,
    name_kr TEXT,
    name_en TEXT,
    market TEXT,

    -- 비즈니스 해석
    business_summary TEXT,
    revenue_structure TEXT,  -- JSON
    moat_type TEXT,  -- JSON list
    moat_description TEXT,
    moat_durability TEXT CHECK(moat_durability IN (
        'STRENGTHENING','STABLE','ERODING'
    )),
    competitors TEXT,  -- JSON list

    -- 투자 분석
    investment_thesis TEXT,
    contrarian_angle TEXT,
    applied_frameworks TEXT,  -- JSON: [1, 8, 17]
    framework_rationale TEXT,

    -- 밸류에이션 맥락
    current_price REAL,
    current_price_date TEXT,
    per_band_position REAL,
    pbr_band_position REAL,
    valuation_summary TEXT,

    -- 변화율/비교
    revenue_qoq REAL,
    revenue_yoy REAL,
    revenue_vs_consensus REAL,
    op_income_qoq REAL,
    op_income_yoy REAL,
    eps_vs_consensus REAL,

    -- 목표주가
    target_bull REAL,
    target_base REAL,
    target_bear REAL,
    target_assumptions TEXT,  -- JSON

    -- 매크로 연동
    macro_exposures TEXT,  -- JSON
    macro_sensitivity TEXT,  -- JSON

    -- 센티먼트
    news_sentiment TEXT CHECK(news_sentiment IN (
        'VERY_NEGATIVE','NEGATIVE','NEUTRAL',
        'POSITIVE','VERY_POSITIVE'
    )),
    news_summary TEXT,

    -- 판단
    verdict TEXT CHECK(verdict IN ('BUY','WATCH','AVOID')),
    conviction TEXT CHECK(conviction IN ('HIGH','MEDIUM','LOW')),
    holding_horizon TEXT,
    stop_condition TEXT,
    risks TEXT,  -- JSON
    risk_severity TEXT,  -- JSON

    -- ROIC/자본배분
    roic REAL,
    wacc REAL,
    roic_wacc_spread REAL,
    capital_allocation_score TEXT,
    reinvestment_rate REAL,

    -- 상태
    article_status TEXT CHECK(article_status IN (
        'NONE','DRAFT','PUBLISHED','NEEDS_UPDATE','ARCHIVED'
    )),
    last_analyzed TEXT,
    analysis_version INTEGER DEFAULT 1
)""",

    'analytical_notes': """
CREATE TABLE IF NOT EXISTS analytical_notes (
    note_id TEXT PRIMARY KEY,
    entity_type TEXT CHECK(entity_type IN (
        'company','industry','policy','macro','theme'
    )),
    entity_id TEXT,
    thesis TEXT,
    consensus_view TEXT,
    counter_view TEXT,
    key_mechanism TEXT,  -- JSON list
    frames TEXT,  -- JSON: ["자본 사이클형","병목 인프라형"]
    risks TEXT,  -- JSON list
    checkpoints TEXT,  -- JSON list
    needed_metrics TEXT,  -- JSON list
    updated_at TEXT DEFAULT (datetime('now'))
)""",

    'macro_events': """
CREATE TABLE IF NOT EXISTS macro_events (
    event_id TEXT PRIMARY KEY,
    event_date TEXT,
    category TEXT,
    title TEXT,
    description TEXT,
    interpretation TEXT,
    affected_tickers TEXT,  -- JSON
    severity TEXT CHECK(severity IN ('HIGH','MEDIUM','LOW')),
    frames TEXT,  -- JSON: applied philosophy frames
    action_taken INTEGER DEFAULT 0,
    analyzed_at TEXT DEFAULT (datetime('now'))
)""",

    'content_log': """
CREATE TABLE IF NOT EXISTS content_log (
    content_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    content_type TEXT CHECK(content_type IN (
        'TIER1_NEW','TIER2_UPDATE','TIER3_REFORMAT'
    )),
    title TEXT,
    platform TEXT,
    published_at TEXT,
    url TEXT,
    needs_update INTEGER DEFAULT 0,
    update_trigger TEXT,
    created_at TEXT DEFAULT (datetime('now'))
)""",

    'verdict_history': """
CREATE TABLE IF NOT EXISTS verdict_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    verdict_date TEXT,
    verdict TEXT,
    conviction TEXT,
    target_base REAL,
    price_at_verdict REAL,
    rationale TEXT,
    applied_frameworks TEXT,  -- JSON
    created_at TEXT DEFAULT (datetime('now'))
)""",

    'style_benchmarks': """
CREATE TABLE IF NOT EXISTS style_benchmarks (
    benchmark_id TEXT PRIMARY KEY,
    source_url TEXT,
    title TEXT,
    intro_style TEXT,
    structure_type TEXT,
    tone TEXT,
    length INTEGER,
    engagement_metric TEXT,  -- JSON
    memo TEXT,
    collected_at TEXT DEFAULT (datetime('now'))
)""",

}


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    for table_name, ddl in TABLES.items():
        cur.execute(ddl)
    conn.commit()


def print_summary(conn: sqlite3.Connection) -> None:
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    print("\n=== 3층: 해석/지식 레이어 ===\n")
    print(f"{'테이블':<25s} {'컬럼 수':>6s}")
    print("-" * 35)
    for (table_name,) in tables:
        col_count = len(
            conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        )
        print(f"  {table_name:<23s} {col_count:>4d}")
    print("-" * 35)
    print(f"  총 {len(tables)}개 테이블 생성 완료\n")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"DB 경로: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    print("테이블 생성 중...")
    create_tables(conn)
    print_summary(conn)

    conn.close()


if __name__ == "__main__":
    main()
