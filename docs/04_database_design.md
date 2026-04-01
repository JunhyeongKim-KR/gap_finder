# 4. 데이터베이스 설계안

## 핵심 테이블: stock_master

```
[기본 정보]
- ticker              : str     # 종목코드 (005930.KS / AAPL)
- name_kr             : str     # 한글 종목명
- name_en             : str     # 영문 종목명
- market              : enum    # KR_KOSPI / KR_KOSDAQ / US_NYSE / US_NASDAQ
- sector              : str     # 산업 분류 (GICS 기준)
- sub_sector          : str     # 세부 업종
- market_cap          : float   # 시가총액 (원/USD)
- market_cap_date     : date    # 시총 기준일

[비즈니스 모델]
- business_summary    : text    # 사업 개요 (3~5문장)
- revenue_structure   : json    # 매출 구성 {"제품A": 40%, "서비스B": 35%}
- key_products        : list    # 핵심 제품/서비스
- customer_segments   : list    # 주요 고객군
- competitors         : list    # 주요 경쟁사
- moat_type           : list    # 해자 유형 [브랜드/네트워크효과/전환비용/규모/특허/규제]
- moat_description    : text    # 해자 설명

[투자 분석]
- investment_thesis   : text    # 핵심 투자 포인트
- thesis_type         : enum    # 7가지 taxonomy 중 택1
- contrarian_angle    : text    # 시장 컨센서스 vs 내 판단 차이
- risks               : list    # 주요 리스크 요인
- risk_severity       : json    # 리스크별 심각도

[밸류에이션]
- valuation_framework : enum    # 컨센서스참고형 / 절대가치평가형 / 상대가치평가형 / 이벤트리버전형
- current_price       : float   # 현재가
- current_price_date  : date    # 기준일
- current_per         : float
- current_pbr         : float
- hist_per_band       : json    # 5년 PER 밴드
- hist_pbr_band       : json    # 5년 PBR 밴드

[목표주가 시나리오]
- target_bull         : float
- target_base         : float
- target_bear         : float
- target_assumptions  : json    # 시나리오별 가정
- upside_pct          : float

[철회 조건]
- stop_condition      : text    # 가설 붕괴 조건
- stop_price          : float   # 참고 손절가
- stop_triggers       : list

[판단]
- verdict             : enum    # BUY / WATCH / AVOID
- conviction          : enum    # HIGH / MEDIUM / LOW
- holding_horizon     : str
- verdict_date        : date
- verdict_history     : list    # [{date, verdict, reason}]

[콘텐츠 관리]
- article_status      : enum    # DRAFT / PUBLISHED / NEEDS_UPDATE / ARCHIVED
- first_published     : date
- last_updated        : date
- update_log          : list
- platform_urls       : json

[매크로 연동]
- macro_exposures     : list    # [금리, 환율_원달러, 유가, ...]
- macro_sensitivity   : json    # {금리: HIGH_NEG, 유가: MID_POS}
```

## 보조 테이블

### financials (분기별 시계열)
```sql
CREATE TABLE financials (
  ticker TEXT, fiscal_period TEXT,
  revenue REAL, operating_income REAL, net_income REAL,
  eps REAL, bps REAL, roe REAL, debt_ratio REAL,
  ocf REAL, fcf REAL, per REAL, pbr REAL, ev_ebitda REAL,
  source TEXT, collected_at TEXT
);
```

### price_daily (일별 시세)
```sql
CREATE TABLE price_daily (
  ticker TEXT, date TEXT,
  open REAL, high REAL, low REAL, close REAL,
  volume INTEGER, market_cap REAL
);
```

### macro_events
```sql
CREATE TABLE macro_events (
  event_id TEXT, event_date TEXT, category TEXT,
  title TEXT, description TEXT,
  affected_tags_json TEXT, severity TEXT, action_taken INTEGER
);
```

### content_log (발행 이력)
```sql
CREATE TABLE content_log (
  ticker TEXT, content_type TEXT, title TEXT,
  platform TEXT, published_at TEXT,
  url TEXT, needs_update INTEGER, update_trigger TEXT
);
```

## 구현 단계

| 단계 | 도구 | 시점 |
|---|---|---|
| 초기 | Google Sheets + SQLite | 지금 바로 |
| 중기 | SQLite + n8n 연동 | 3개월차 |
| 장기 | Baserow(self-hosted) 또는 PostgreSQL | 6개월차 검토 |
