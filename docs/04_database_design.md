# 4. 데이터베이스 설계

> 최종 수정: 2026-04-04
> 상태: 기존 5테이블 운영 중 / 확장 설계 확정

---

## 설계 원칙

> **"철학은 프롬프트에, 사실은 DB에"**

| 레이어 | 역할 | 위치 |
|--------|------|------|
| Agent 프롬프트 | 해석 엔진 — 22개 투자 프레임, 글쓰기 원칙 | `docs/12`, `docs/13` |
| DB | 사실 저장소 — 재무, 시세, 거시, 컨센서스 등 | `db/gapfinder.db` |

- Agent 프롬프트는 **데이터를 어떤 관점으로 해석할지** 결정한다 (정적).
- DB는 Agent가 해석할 **재료(사실 데이터)** 를 저장한다 (동적).
- 이 분리는 관심사 분리(Separation of Concerns) 원칙에 기반한다.
- `stock_master.applied_frameworks` 필드로 각 종목에 어떤 프레임(docs/12)을 적용했는지 추적한다.

---

## 기존 테이블 (구현 완료 — init_db.py 기준)

### 1. stock_master — 종목 마스터

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

### 2. financials — 분기별 재무 시계열

```sql
CREATE TABLE financials (
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
```

### 3. price_daily — 일별 시세

```sql
CREATE TABLE price_daily (
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
```

### 4. macro_events — 거시/이벤트

```sql
CREATE TABLE macro_events (
  event_id            TEXT PRIMARY KEY,
  event_date          TEXT,
  category            TEXT,
  title               TEXT,
  description         TEXT,
  affected_tags_json  TEXT,
  severity            TEXT,
  action_taken        INTEGER DEFAULT 0
);
```

### 5. content_log — 발행 이력

```sql
CREATE TABLE content_log (
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
```

---

## stock_master 확장 예정 필드

> Phase 2에서 기존 stock_master에 ALTER TABLE로 추가할 필드.

```sql
-- 자본 효율성 (CEO 범주 E 심화)
ALTER TABLE stock_master ADD COLUMN roic                    REAL;    -- 투하자본수익률
ALTER TABLE stock_master ADD COLUMN wacc                    REAL;    -- 가중평균자본비용
ALTER TABLE stock_master ADD COLUMN roic_wacc_spread        REAL;    -- ROIC - WACC (초과수익 스프레드)

-- 해자 지속성 (프레임 #12 해자 지속성형)
ALTER TABLE stock_master ADD COLUMN moat_durability         TEXT;    -- 해자 침식 여부 평가

-- 성장 활주로 (프레임 #13 퀄리티 복리형)
ALTER TABLE stock_master ADD COLUMN reinvestment_rate       REAL;    -- 재투자율
ALTER TABLE stock_master ADD COLUMN growth_runway           TEXT;    -- 성장 활주로 정성 평가

-- 자본배분 (프레임 #10 자본배분형)
ALTER TABLE stock_master ADD COLUMN capital_allocation_score TEXT;   -- 자본배분 종합 평가

-- 프레임 추적
ALTER TABLE stock_master ADD COLUMN applied_frameworks      TEXT;    -- JSON array: docs/12에서 적용한 프레임 번호 리스트
```

---

## 확장 예정 테이블 (CTO 액션플랜 Phase 2)

### 6. consensus — 컨센서스/기대치 데이터

> CEO 데이터 범주 G 대응. 프레임 #17(기대치 역산형)의 핵심 입력 데이터.

```sql
CREATE TABLE consensus (
  ticker              TEXT NOT NULL,
  date                TEXT NOT NULL,       -- 기준일
  analyst_count       INTEGER,             -- 커버 애널리스트 수
  buy_count           INTEGER,             -- 매수 의견 수
  hold_count          INTEGER,             -- 중립 의견 수
  sell_count          INTEGER,             -- 매도 의견 수
  target_price_avg    REAL,                -- 목표주가 평균
  target_price_high   REAL,                -- 목표주가 최고
  target_price_low    REAL,                -- 목표주가 최저
  eps_estimate        REAL,                -- EPS 컨센서스
  revenue_estimate    REAL,                -- 매출 컨센서스
  surprise_history    TEXT,                -- JSON: 최근 서프라이즈/쇼크 이력
  source              TEXT,
  collected_at        TEXT,
  PRIMARY KEY (ticker, date),
  FOREIGN KEY (ticker) REFERENCES stock_master(ticker)
);
```

### 7. management — 경영진/자본배분 데이터

> CEO 데이터 범주 F 대응. 프레임 #14(경영자 DNA형), #10(자본배분형)의 핵심 입력 데이터.

```sql
CREATE TABLE management (
  ticker                    TEXT NOT NULL,
  ceo_name                  TEXT,                -- CEO 이름
  ceo_stake_pct             REAL,                -- CEO 지분율 (%)
  insider_buy_sell           TEXT,                -- JSON: 최근 내부자 매매 내역
  compensation_structure     TEXT,                -- 보상 구조 설명
  tsr_linked                INTEGER DEFAULT 0,   -- TSR 연동 여부 (0/1)
  capital_allocation_history TEXT,                -- JSON: CAPEX/M&A/배당/자사주 이력
  shareholder_letter_summary TEXT,                -- 주주서한 요약
  source                    TEXT,
  collected_at              TEXT,
  updated_at                TEXT,
  PRIMARY KEY (ticker),
  FOREIGN KEY (ticker) REFERENCES stock_master(ticker)
);
```

### 8. industry_cycle — 산업 구조/공급 데이터

> CEO 데이터 범주 B 대응. 프레임 #1(자본 사이클형)의 핵심 입력 데이터.

```sql
CREATE TABLE industry_cycle (
  sector                TEXT NOT NULL,       -- 산업 분류
  date                  TEXT NOT NULL,       -- 기준일
  capex_total           REAL,                -- 업종 전체 CAPEX
  depreciation          REAL,                -- 업종 전체 감가상각
  capex_da_ratio        REAL,                -- CAPEX / D&A 비율
  new_entrants          INTEGER,             -- 신규 진입 기업 수
  ipo_count             INTEGER,             -- IPO 건수
  capacity_utilization  REAL,                -- 가동률 (%)
  inventory_level       REAL,                -- 재고 수준
  price_competition     TEXT,                -- 가격 경쟁 강도 (HIGH/MID/LOW)
  source                TEXT,
  collected_at          TEXT,
  PRIMARY KEY (sector, date)
);
```

---

## CEO 데이터 범주 A~J 매핑표

CEO가 정의한 10개 데이터 범주가 어떤 테이블에 저장되는지 매핑.

| 범주 | 내용 | 저장 테이블 | 비고 |
|------|------|-------------|------|
| **A. 거시/국제정세** | 금리, 물가, 환율, 유가, 관세, 외교 | `macro_events` | 기존 테이블 활용 |
| **B. 산업 구조/공급** | CAPEX, D&A, IPO, 가동률, 재고 | `industry_cycle` (**신규**) | 자본 사이클 프레임 핵심 |
| **C. 정책/제도/거버넌스** | 법적 구조, 허가제, API 표준 | `macro_events` (장기 별도 검토) | 정성 데이터 → 구조화 난이도 높음 |
| **D. 자원/에너지/광물** | 우라늄, 구리, 리튬, 원전, SMR | `macro_events` (확장) | category 필드로 구분 |
| **E. 기업 재무/가치** | 매출~FCF, 밸류에이션, ROIC/WACC | `financials` + `stock_master` 확장 | 기존 테이블 + 신규 필드 |
| **F. 경영진/자본배분** | CEO 지분, 내부자 매매, 보상 구조 | `management` (**신규**) | 경영자 DNA 프레임 핵심 |
| **G. 기대치/컨센서스** | 애널리스트 전망, 가이던스, 서프라이즈 | `consensus` (**신규**) | 기대치 역산 프레임 핵심 |
| **H. 이벤트 대응** | 이벤트→시장 반응→후속 | `macro_events` | 기존 테이블 활용, severity로 구분 |
| **I. 데이터/AI/클라우드** | 인프라형 + 선행수요형 | `stock_master` + `financials` | 개별 종목 분석 시 반영 |
| **J. 스타일/콘텐츠 개선** | 제목, 길이, 조회수, 스타일 | `content_log` (확장 예정) | Phase 4에서 필드 추가 |

---

## 구현 우선순위

CTO 액션플랜(2026-04-04)에 따른 데이터 범주별 구현 일정.

| 우선순위 | 범주 | 대상 테이블 | 이유 |
|----------|------|-------------|------|
| **즉시** | E(기업 재무) | `financials` + `stock_master` 확장 | 글 생성에 직접 필요, yfinance 자동화 가능 |
| **즉시** | G(컨센서스) | `consensus` 신규 생성 | 기대치 역산 프레임에 필수 |
| **1개월 내** | A(거시) | `macro_events` 강화 | 뉴스/공시 크롤링 연동 시 |
| **1개월 내** | F(경영진) | `management` 신규 생성 | 경영자 DNA 프레임에 필수 |
| **1개월 내** | H(이벤트) | `macro_events` 활용 | 기존 테이블 구조로 수용 가능 |
| **2~3개월** | B(산업) | `industry_cycle` 신규 생성 | 수동 입력 + 반자동 수집 혼합 |
| **2~3개월** | D(자원) | `macro_events` 확장 | category 필드로 구분 |
| **장기** | C(정책/거버넌스) | 별도 테이블 검토 | 정성 데이터 많아 구조화 난이도 높음 |
| **장기** | I(인프라 기업) | 기존 테이블 활용 | 종목별 분석 시 stock_master에 반영 |
| **장기** | J(스타일) | `content_log` 확장 | Phase 4 스타일 최적화 시 |

---

## 구현 단계

| 단계 | 도구 | 시점 | 테이블 |
|------|------|------|--------|
| 초기 (현재) | SQLite (`db/gapfinder.db`) | 운영 중 | stock_master, financials, price_daily, macro_events, content_log |
| Phase 2 | SQLite + ALTER TABLE / CREATE TABLE | 즉시~1개월 | + consensus, management, stock_master 확장 필드 |
| Phase 2 후반 | SQLite + 크롤링 스크립트 강화 | 2~3개월 | + industry_cycle |
| 중기 | SQLite + n8n 연동 | 3개월차 | 전체 8테이블 자동 수집 |
| 장기 | Baserow(self-hosted) 또는 PostgreSQL | 6개월차 검토 | 마이그레이션 검토 |

---

## 용량 예측

### 기존 테이블

| 테이블 | 1종목/연간 | 50종목/3년 | 비고 |
|--------|------------|------------|------|
| stock_master | 1행 | 50행 | 종목 마스터 |
| financials | 4행 | 600행 | 분기별 |
| price_daily | 250행 | 37,500행 | 영업일 기준 |
| macro_events | — | ~500행 | 주요 이벤트만 |
| content_log | — | ~200행 | 발행 건수 |

### 확장 테이블 (추가분)

| 테이블 | 1종목/연간 | 50종목/3년 | 비고 |
|--------|------------|------------|------|
| consensus | 12행 | 1,800행 | 월별 스냅샷 |
| management | 1행 | 50행 | 종목당 1행, 수시 업데이트 |
| industry_cycle | — | ~600행 | 섹터 x 월별 (약 10섹터) |

### 합계

- 기존: ~39,000행 (50종목 3년 기준)
- 확장 후: ~41,500행
- SQLite로 충분히 처리 가능한 규모 (수백만 행까지 문제없음)
