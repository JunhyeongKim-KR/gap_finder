#!/usr/bin/env python3
"""GapFinder enriched.db 초기화 스크립트.

enriched.db는 재해석(reinterpret) Agent가 생성하는 분석 결과를 저장하는 DB이다.
- 재해석 Agent: raw.db + 철학.md → enriched.db (투자 분석, 프레임 적용, 시나리오 등)
- 글쓰기 Agent: enriched.db → 콘텐츠 발행

테이블 구성:
  1. stock_analysis   — 종목별 재해석 결과 마스터
  2. macro_events     — 매크로 이벤트 해석
  3. content_log      — 콘텐츠 발행 이력
  4. verdict_history   — 판단 이력 (트랙레코드)
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "enriched.db"


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # 1. stock_analysis — 종목 분석 마스터 (재해석 Agent가 생성/업데이트)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_analysis (
        ticker TEXT PRIMARY KEY,
        name_kr TEXT,
        name_en TEXT,
        market TEXT,

        -- 비즈니스 모델 해석
        business_summary TEXT,
        revenue_structure TEXT,          -- JSON
        moat_type TEXT,                  -- JSON list
        moat_description TEXT,
        moat_durability TEXT CHECK(moat_durability IN ('STRENGTHENING','STABLE','ERODING')),
        competitors TEXT,                -- JSON list

        -- 투자 분석 (재해석 결과)
        investment_thesis TEXT,
        contrarian_angle TEXT,
        applied_frameworks TEXT,         -- JSON: [1, 8, 17] 적용된 프레임 번호
        framework_rationale TEXT,        -- 프레임 선택 근거

        -- 밸류에이션 맥락
        current_price REAL,
        current_price_date TEXT,
        per_band_position REAL,          -- 0~100 (5년 밴드 내 위치)
        pbr_band_position REAL,
        valuation_summary TEXT,          -- "밴드 하단 20%, 업종 대비 30% 할인"

        -- 변화율/비교 (재해석 핵심)
        revenue_qoq REAL,
        revenue_yoy REAL,
        revenue_vs_consensus REAL,       -- 서프라이즈 %
        op_income_qoq REAL,
        op_income_yoy REAL,
        eps_vs_consensus REAL,

        -- 목표주가 시나리오
        target_bull REAL,
        target_base REAL,
        target_bear REAL,
        target_assumptions TEXT,         -- JSON

        -- 매크로 연동
        macro_exposures TEXT,            -- JSON: ["금리", "환율_원달러", "유가"]
        macro_sensitivity TEXT,          -- JSON: {"금리": "HIGH_NEG", "유가": "MID_POS"}

        -- 뉴스 센티먼트 요약
        news_sentiment TEXT CHECK(news_sentiment IN ('VERY_NEGATIVE','NEGATIVE','NEUTRAL','POSITIVE','VERY_POSITIVE')),
        news_summary TEXT,

        -- 판단
        verdict TEXT CHECK(verdict IN ('BUY','WATCH','AVOID')),
        conviction TEXT CHECK(conviction IN ('HIGH','MEDIUM','LOW')),
        holding_horizon TEXT,
        stop_condition TEXT,

        -- 리스크
        risks TEXT,                      -- JSON list
        risk_severity TEXT,              -- JSON

        -- 콘텐츠 상태
        article_status TEXT CHECK(article_status IN ('NONE','DRAFT','PUBLISHED','NEEDS_UPDATE','ARCHIVED')),

        -- 메타
        last_analyzed TEXT,
        analysis_version INTEGER DEFAULT 1,

        -- ROIC/자본배분
        roic REAL,
        wacc REAL,
        roic_wacc_spread REAL,
        capital_allocation_score TEXT,
        reinvestment_rate REAL
    );
    """)

    # 2. macro_events — 매크로 이벤트 해석
    cur.execute("""
    CREATE TABLE IF NOT EXISTS macro_events (
        event_id TEXT PRIMARY KEY,
        event_date TEXT,
        category TEXT,
        title TEXT,
        description TEXT,
        interpretation TEXT,             -- 재해석 Agent의 해석
        affected_tickers TEXT,           -- JSON list
        severity TEXT CHECK(severity IN ('HIGH','MEDIUM','LOW')),
        action_taken INTEGER DEFAULT 0,
        analyzed_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # 3. content_log — 발행 이력
    cur.execute("""
    CREATE TABLE IF NOT EXISTS content_log (
        content_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        content_type TEXT CHECK(content_type IN ('TIER1_NEW','TIER2_UPDATE','TIER3_REFORMAT')),
        title TEXT,
        platform TEXT,
        published_at TEXT,
        url TEXT,
        needs_update INTEGER DEFAULT 0,
        update_trigger TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    # 4. verdict_history — 판단 이력 (트랙레코드)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS verdict_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT,
        verdict_date TEXT,
        verdict TEXT,
        conviction TEXT,
        target_base REAL,
        price_at_verdict REAL,
        rationale TEXT,
        applied_frameworks TEXT,         -- JSON
        created_at TEXT DEFAULT (datetime('now'))
    );
    """)

    conn.commit()


def print_summary(conn: sqlite3.Connection) -> None:
    """생성된 테이블과 컬럼 수를 출력한다."""
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()

    print(f"\n{'테이블':<25s} {'컬럼 수':>6s}")
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
