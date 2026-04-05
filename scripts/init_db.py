#!/usr/bin/env python3
# DEPRECATED: 이 스크립트는 더 이상 사용되지 않습니다. init_raw_db.py / init_enriched_db.py를 사용하세요.
"""GapFinder SQLite DB 초기화 스크립트.

docs/04_database_design.md 기준으로 5개 테이블을 생성한다.
"""

import sqlite3
import os
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "gapfinder.db"


def create_tables(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    # 1. stock_master — 종목 마스터 (모든 필드를 docs/04 그대로 반영)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_master (
        ticker              TEXT PRIMARY KEY,
        name_kr             TEXT,
        name_en             TEXT,
        market              TEXT CHECK(market IN (
            'KR_KOSPI','KR_KOSDAQ','US_NYSE','US_NASDAQ')),
        sector              TEXT,
        sub_sector          TEXT,
        market_cap          REAL,
        market_cap_date     TEXT,

        -- 비즈니스 모델
        business_summary    TEXT,
        revenue_structure   TEXT,  -- JSON
        key_products        TEXT,  -- JSON array
        customer_segments   TEXT,  -- JSON array
        competitors         TEXT,  -- JSON array
        moat_type           TEXT,  -- JSON array
        moat_description    TEXT,

        -- 투자 분석
        investment_thesis   TEXT,
        thesis_type         TEXT CHECK(thesis_type IN (
            '규제과민반응','일회성실적쇼크','업황저점',
            '컨센서스역이용','낙폭과대','구조적경쟁우위오판','공급축소소외섹터')),
        contrarian_angle    TEXT,
        risks               TEXT,  -- JSON array
        risk_severity       TEXT,  -- JSON

        -- 밸류에이션
        valuation_framework TEXT CHECK(valuation_framework IN (
            '컨센서스참고형','절대가치평가형','상대가치평가형','이벤트리버전형')),
        current_price       REAL,
        current_price_date  TEXT,
        current_per         REAL,
        current_pbr         REAL,
        hist_per_band       TEXT,  -- JSON
        hist_pbr_band       TEXT,  -- JSON

        -- 목표주가 시나리오
        target_bull         REAL,
        target_base         REAL,
        target_bear         REAL,
        target_assumptions  TEXT,  -- JSON
        upside_pct          REAL,

        -- 철회 조건
        stop_condition      TEXT,
        stop_price          REAL,
        stop_triggers       TEXT,  -- JSON array

        -- 판단
        verdict             TEXT CHECK(verdict IN ('BUY','WATCH','AVOID')),
        conviction          TEXT CHECK(conviction IN ('HIGH','MEDIUM','LOW')),
        holding_horizon     TEXT,
        verdict_date        TEXT,
        verdict_history     TEXT,  -- JSON array

        -- 콘텐츠 관리
        article_status      TEXT CHECK(article_status IN (
            'DRAFT','PUBLISHED','NEEDS_UPDATE','ARCHIVED')),
        first_published     TEXT,
        last_updated        TEXT,
        update_log          TEXT,  -- JSON array
        platform_urls       TEXT,  -- JSON

        -- 매크로 연동
        macro_exposures     TEXT,  -- JSON array
        macro_sensitivity   TEXT   -- JSON
    );
    """)

    # 2. financials — 분기별 재무 시계열
    cur.execute("""
    CREATE TABLE IF NOT EXISTS financials (
        ticker          TEXT NOT NULL,
        fiscal_period   TEXT NOT NULL,
        revenue         REAL,
        operating_income REAL,
        net_income      REAL,
        eps             REAL,
        bps             REAL,
        roe             REAL,
        debt_ratio      REAL,
        ocf             REAL,
        fcf             REAL,
        per             REAL,
        pbr             REAL,
        ev_ebitda       REAL,
        source          TEXT,
        collected_at    TEXT,
        PRIMARY KEY (ticker, fiscal_period),
        FOREIGN KEY (ticker) REFERENCES stock_master(ticker)
    );
    """)

    # 3. price_daily — 일별 시세
    cur.execute("""
    CREATE TABLE IF NOT EXISTS price_daily (
        ticker      TEXT NOT NULL,
        date        TEXT NOT NULL,
        open        REAL,
        high        REAL,
        low         REAL,
        close       REAL,
        volume      INTEGER,
        market_cap  REAL,
        PRIMARY KEY (ticker, date),
        FOREIGN KEY (ticker) REFERENCES stock_master(ticker)
    );
    """)

    # 4. macro_events
    cur.execute("""
    CREATE TABLE IF NOT EXISTS macro_events (
        event_id            TEXT PRIMARY KEY,
        event_date          TEXT,
        category            TEXT,
        title               TEXT,
        description         TEXT,
        affected_tags_json  TEXT,
        severity            TEXT,
        action_taken        INTEGER DEFAULT 0
    );
    """)

    # 5. content_log — 발행 이력
    cur.execute("""
    CREATE TABLE IF NOT EXISTS content_log (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker          TEXT,
        content_type    TEXT,
        title           TEXT,
        platform        TEXT,
        published_at    TEXT,
        url             TEXT,
        needs_update    INTEGER DEFAULT 0,
        update_trigger  TEXT,
        FOREIGN KEY (ticker) REFERENCES stock_master(ticker)
    );
    """)

    conn.commit()


def seed_sample_stock(conn: sqlite3.Connection) -> None:
    """샘플 종목 1개(삼성전자)를 입력한다."""
    cur = conn.cursor()

    # 이미 존재하면 스킵
    cur.execute("SELECT 1 FROM stock_master WHERE ticker = '005930.KS'")
    if cur.fetchone():
        print("  샘플 종목(005930.KS) 이미 존재 — 스킵")
        return

    cur.execute("""
    INSERT INTO stock_master VALUES (
        '005930.KS',            -- ticker
        '삼성전자',              -- name_kr
        'Samsung Electronics',  -- name_en
        'KR_KOSPI',             -- market
        'Information Technology', -- sector (GICS)
        '반도체',                -- sub_sector
        3200000.0,              -- market_cap (억원, 약 320조)
        '2026-03-31',           -- market_cap_date

        -- 비즈니스 모델
        '글로벌 1위 메모리 반도체(DRAM/NAND) 제조사. 파운드리, 디스플레이, 스마트폰(갤럭시), 가전까지 수직계열화된 종합 전자기업. HBM 수요 확대에 따른 메모리 업사이클 수혜 기대.',
        ?,  -- revenue_structure
        ?,  -- key_products
        ?,  -- customer_segments
        ?,  -- competitors
        ?,  -- moat_type
        '글로벌 메모리 시장 40%+ 점유율, 반도체 미세공정 기술력, 수직계열화를 통한 원가 경쟁력, 대규모 CAPEX 투자 능력이 신규 진입을 억제.',

        -- 투자 분석
        'HBM3E/HBM4 양산 본격화에 따른 메모리 ASP 상승과 파운드리 수율 개선이 시장 기대 대비 빠르게 진행 중. 현재 주가는 메모리 다운사이클 우려를 과도하게 반영.',
        '업황저점',
        '시장은 메모리 업황 둔화와 파운드리 경쟁력 부족을 반영해 역사적 PBR 하단에서 거래 중. 그러나 AI 서버향 HBM 수요는 구조적이며, 2026년 하반기 DRAM 가격 반등이 컨센서스보다 빠를 가능성.',
        ?,  -- risks
        ?,  -- risk_severity

        -- 밸류에이션
        '상대가치평가형',
        55000,                  -- current_price (원)
        '2026-03-31',
        11.5,                   -- current_per
        1.05,                   -- current_pbr
        ?,  -- hist_per_band
        ?,  -- hist_pbr_band

        -- 목표주가 시나리오
        80000,                  -- target_bull
        70000,                  -- target_base
        50000,                  -- target_bear
        ?,  -- target_assumptions
        27.3,                   -- upside_pct (기본 시나리오 기준)

        -- 철회 조건
        'HBM 수율 문제가 2분기 연속 미해결 또는 DRAM 고정거래가격 3분기 연속 하락 시 투자 논리 재검토',
        48000,
        ?,  -- stop_triggers

        -- 판단
        'BUY',
        'MEDIUM',
        '6~12개월',
        '2026-03-31',
        ?,  -- verdict_history

        -- 콘텐츠 관리
        'DRAFT',
        NULL,
        '2026-03-31',
        NULL,
        NULL,

        -- 매크로 연동
        ?,  -- macro_exposures
        ?   -- macro_sensitivity
    )
    """, (
        json.dumps({"메모리반도체": 45, "파운드리": 15, "디스플레이": 10, "MX(모바일)": 25, "기타": 5}, ensure_ascii=False),
        json.dumps(["DRAM", "NAND Flash", "HBM", "파운드리", "갤럭시 스마트폰", "OLED 패널"], ensure_ascii=False),
        json.dumps(["글로벌 IT기업(애플, 구글 등)", "데이터센터(AWS, MS)", "통신사", "일반 소비자"], ensure_ascii=False),
        json.dumps(["SK하이닉스", "Micron", "TSMC", "Intel"], ensure_ascii=False),
        json.dumps(["규모의 경제", "기술력(미세공정)", "수직계열화", "브랜드"], ensure_ascii=False),
        json.dumps(["중국 반도체 굴기로 메모리 가격 구조적 하락", "파운드리 수율 개선 지연", "HBM 경쟁 심화(SK하이닉스 우위 지속)", "글로벌 경기침체로 IT 수요 감소"], ensure_ascii=False),
        json.dumps({"중국_반도체": "MID_NEG", "파운드리_수율": "HIGH_NEG", "HBM_경쟁": "MID_NEG", "글로벌_경기": "HIGH_NEG"}, ensure_ascii=False),
        json.dumps({"5년_low": 8.0, "5년_high": 18.0, "현재": 11.5}, ensure_ascii=False),
        json.dumps({"5년_low": 0.9, "5년_high": 1.8, "현재": 1.05}, ensure_ascii=False),
        json.dumps({
            "낙관": "HBM4 조기 양산 + DRAM 가격 30%↑ → PER 14배 적용",
            "기본": "HBM3E 정상 양산 + DRAM 가격 15%↑ → PER 12배 적용",
            "비관": "HBM 수율 지연 + DRAM 가격 보합 → PER 10배 적용"
        }, ensure_ascii=False),
        json.dumps(["HBM 수율 2분기 연속 미달", "DRAM 고정가 3분기 연속 하락", "파운드리 대형 고객 이탈"], ensure_ascii=False),
        json.dumps([{"date": "2026-03-31", "verdict": "BUY", "reason": "초기 분석 — HBM 업사이클 + PBR 밴드 하단"}], ensure_ascii=False),
        json.dumps(["금리", "환율_원달러", "반도체_업황", "AI_수요"], ensure_ascii=False),
        json.dumps({"금리": "MID_NEG", "환율_원달러": "HIGH_NEG", "반도체_업황": "HIGH_POS", "AI_수요": "HIGH_POS"}, ensure_ascii=False),
    ))

    # 샘플 재무 데이터
    financials_data = [
        ("005930.KS", "2025Q1", 77.0, 6.6, 5.1, 340, 42000, 5.5, 80, 15.0, 8.0, 16.0, 1.2, 7.5, "DART", "2026-03-31"),
        ("005930.KS", "2025Q2", 74.0, 10.4, 8.0, 530, 43000, 7.8, 78, 18.0, 10.0, 12.5, 1.15, 6.8, "DART", "2026-03-31"),
        ("005930.KS", "2025Q3", 79.0, 12.3, 9.8, 650, 44000, 9.0, 76, 20.0, 12.0, 10.8, 1.1, 6.2, "DART", "2026-03-31"),
        ("005930.KS", "2025Q4", 75.0, 8.0, 6.5, 430, 44500, 7.2, 77, 16.0, 9.0, 13.0, 1.08, 7.0, "DART", "2026-03-31"),
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO financials
        (ticker, fiscal_period, revenue, operating_income, net_income,
         eps, bps, roe, debt_ratio, ocf, fcf, per, pbr, ev_ebitda,
         source, collected_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, financials_data)

    # 샘플 시세 (최근 5일)
    price_data = [
        ("005930.KS", "2026-03-25", 54500, 55200, 54000, 54800, 15000000, 3270000),
        ("005930.KS", "2026-03-26", 54800, 55500, 54300, 55100, 14500000, 3288000),
        ("005930.KS", "2026-03-27", 55100, 55800, 54800, 55500, 16000000, 3312000),
        ("005930.KS", "2026-03-28", 55500, 56000, 54500, 54800, 18000000, 3270000),
        ("005930.KS", "2026-03-31", 54800, 55300, 54200, 55000, 14000000, 3282000),
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO price_daily
        (ticker, date, open, high, low, close, volume, market_cap)
    VALUES (?,?,?,?,?,?,?,?)
    """, price_data)

    conn.commit()
    print("  샘플 종목(삼성전자 005930.KS) 입력 완료")


def main():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"DB 경로: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")

    print("테이블 생성 중...")
    create_tables(conn)

    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    print(f"  생성된 테이블: {[t[0] for t in tables]}")

    print("샘플 데이터 입력 중...")
    seed_sample_stock(conn)

    conn.close()
    print("완료!")


if __name__ == "__main__":
    main()
