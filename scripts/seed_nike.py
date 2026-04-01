#!/usr/bin/env python3
"""Nike(NKE) 종목 데이터를 gapfinder.db에 추가한다."""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "gapfinder.db"


def seed_nike(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM stock_master WHERE ticker = 'NKE'")
    if cur.fetchone():
        print("  NKE 이미 존재 — 스킵")
        return

    cur.execute("""
    INSERT INTO stock_master VALUES (
        'NKE',                      -- ticker
        '나이키',                    -- name_kr
        'Nike Inc.',                -- name_en
        'US_NYSE',                  -- market
        'Consumer Discretionary',   -- sector (GICS)
        '의류/신발',                 -- sub_sector
        880.0,                      -- market_cap (억 USD → 약 $88B)
        '2026-03-31',               -- market_cap_date

        -- 비즈니스 모델
        '글로벌 1위 스포츠웨어 브랜드. 운동화·의류·장비를 Nike/Jordan/Converse 브랜드로 판매. DTC(Direct-to-Consumer) 전환 가속 중이나 도매 채널 재강화로 전략 수정. 글로벌 소비자 브랜드 파워 1위권.',
        ?,  -- revenue_structure
        ?,  -- key_products
        ?,  -- customer_segments
        ?,  -- competitors
        ?,  -- moat_type
        '50년 이상 쌓아온 글로벌 브랜드 파워, 엘리트 선수 스폰서십(조던/르브론/음바페), 혁신 R&D(에어맥스/줌/플라이니트), 글로벌 유통 인프라가 경쟁사 진입을 억제. 연간 마케팅비 $4B+.',

        -- 투자 분석
        'DTC 전략 과속 후유증과 경쟁 심화로 주가가 2021년 고점 대비 60%+ 하락. 그러나 신임 CEO Elliott Hill의 도매 채널 재정상화 + 혁신 제품 파이프라인 복귀가 시장 기대보다 빠를 가능성.',
        '낙폭과대',
        '시장은 나이키의 성장 둔화를 구조적 문제로 반영 중(On/Hoka 추격, 중국 부진, 재고 문제). 그러나 브랜드 파워는 건재하고, 도매 파트너 복귀 + 혁신 제품(에어맥스 Dn, 페가수스 41) 출시로 2026H2 턴어라운드 시그널 예상.',
        ?,  -- risks
        ?,  -- risk_severity

        -- 밸류에이션
        '상대가치평가형',
        59.0,                       -- current_price (USD)
        '2026-03-31',
        22.0,                       -- current_per (forward)
        7.5,                        -- current_pbr
        ?,  -- hist_per_band
        ?,  -- hist_pbr_band

        -- 목표주가 시나리오
        95.0,                       -- target_bull
        80.0,                       -- target_base
        50.0,                       -- target_bear
        ?,  -- target_assumptions
        35.6,                       -- upside_pct (기본 시나리오)

        -- 철회 조건
        '2분기 연속 매출 역성장 + 북미 DTC 매출 감소 지속 시 브랜드 훼손 우려로 투자 논리 재검토',
        45.0,
        ?,  -- stop_triggers

        -- 판단
        'BUY',
        'MEDIUM',
        '6~12개월',
        '2026-04-01',
        ?,  -- verdict_history

        -- 콘텐츠 관리
        'DRAFT',
        NULL,
        '2026-04-01',
        NULL,
        NULL,

        -- 매크로 연동
        ?,  -- macro_exposures
        ?   -- macro_sensitivity
    )
    """, (
        json.dumps({"신발": 65, "의류": 27, "장비/기타": 8}, ensure_ascii=False),
        json.dumps(["에어맥스", "에어포스1", "덩크", "조던", "페가수스", "컨버스"], ensure_ascii=False),
        json.dumps(["글로벌 일반 소비자", "운동선수/피트니스", "스니커즈 컬렉터", "도매 파트너(풋락커, JD Sports)"], ensure_ascii=False),
        json.dumps(["Adidas", "On Running", "Hoka(Deckers)", "New Balance", "Puma"], ensure_ascii=False),
        json.dumps(["브랜드 파워", "선수 스폰서십", "R&D/혁신", "글로벌 유통망", "규모의 경제"], ensure_ascii=False),
        json.dumps([
            "On/Hoka 등 신흥 브랜드의 러닝 시장 점유율 잠식",
            "중국 소비 부진 + 현지 브랜드(안타/리닝) 부상",
            "DTC 전환 과정에서 도매 파트너 관계 훼손",
            "재고 과잉에 따른 마진 압박",
            "글로벌 경기침체 시 소비 위축"
        ], ensure_ascii=False),
        json.dumps({
            "신흥브랜드_경쟁": "HIGH_NEG",
            "중국_소비": "MID_NEG",
            "도매채널": "HIGH_NEG",
            "재고": "MID_NEG",
            "글로벌_경기": "MID_NEG"
        }, ensure_ascii=False),
        json.dumps({"5년_low": 18.0, "5년_high": 45.0, "현재": 22.0}, ensure_ascii=False),
        json.dumps({"5년_low": 6.0, "5년_high": 18.0, "현재": 7.5}, ensure_ascii=False),
        json.dumps({
            "낙관": "도매 정상화 + 혁신 제품 히트 + 중국 회복 → forward PER 30배",
            "기본": "도매 점진적 회복 + 마진 안정화 → forward PER 25배",
            "비관": "경쟁 심화 지속 + 매출 역성장 → forward PER 18배"
        }, ensure_ascii=False),
        json.dumps([
            "2분기 연속 매출 역성장",
            "북미 DTC 매출 감소 지속",
            "신임 CEO 전략 변경 실패 (도매 복귀 지연)",
            "그로스 마진 40% 하회"
        ], ensure_ascii=False),
        json.dumps([{"date": "2026-04-01", "verdict": "BUY", "reason": "낙폭과대 — 브랜드 건재 + CEO 교체 턴어라운드 기대"}], ensure_ascii=False),
        json.dumps(["금리", "환율_달러", "소비심리", "중국_경기", "원자재_면화"], ensure_ascii=False),
        json.dumps({
            "금리": "MID_NEG",
            "환율_달러": "MID_NEG",
            "소비심리": "HIGH_POS",
            "중국_경기": "HIGH_POS",
            "원자재_면화": "MID_NEG"
        }, ensure_ascii=False),
    ))

    # 재무 데이터 (Nike FY는 6월 결산)
    financials_data = [
        ("NKE", "FY25Q1", 11.6, 1.2, 0.79, 0.52, 8.0, 6.5, 95, 1.8, 0.9, 28.0, 8.5, 18.0, "10-Q", "2026-04-01"),
        ("NKE", "FY25Q2", 12.4, 1.6, 1.16, 0.78, 8.2, 9.3, 90, 2.1, 1.2, 24.0, 8.0, 16.0, "10-Q", "2026-04-01"),
        ("NKE", "FY25Q3", 11.3, 0.9, 0.58, 0.38, 8.0, 4.8, 98, 1.4, 0.5, 32.0, 8.8, 20.0, "10-Q", "2026-04-01"),
        ("NKE", "FY25Q4", 12.0, 1.1, 0.74, 0.49, 8.1, 6.0, 92, 1.9, 1.0, 26.0, 8.2, 17.5, "10-Q", "2026-04-01"),
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO financials
        (ticker, fiscal_period, revenue, operating_income, net_income,
         eps, bps, roe, debt_ratio, ocf, fcf, per, pbr, ev_ebitda,
         source, collected_at)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, financials_data)

    # 시세 데이터
    price_data = [
        ("NKE", "2026-03-25", 57.50, 58.80, 57.00, 58.20, 8500000, 880),
        ("NKE", "2026-03-26", 58.20, 59.50, 57.80, 59.10, 9200000, 893),
        ("NKE", "2026-03-27", 59.10, 60.20, 58.50, 59.80, 10100000, 904),
        ("NKE", "2026-03-28", 59.80, 60.50, 58.00, 58.50, 12000000, 884),
        ("NKE", "2026-03-31", 58.50, 59.50, 58.00, 59.00, 8800000, 892),
    ]
    cur.executemany("""
    INSERT OR IGNORE INTO price_daily
        (ticker, date, open, high, low, close, volume, market_cap)
    VALUES (?,?,?,?,?,?,?,?)
    """, price_data)

    conn.commit()
    print("  Nike(NKE) 입력 완료")


def main():
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys=ON")
    print("Nike 데이터 입력 중...")
    seed_nike(conn)
    conn.close()
    print("완료!")


if __name__ == "__main__":
    main()
