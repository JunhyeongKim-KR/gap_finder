# 크롤링 스크립트 구조

## 설계 원칙

스크립트는 **소스(웹사이트)별이 아니라, 저장 대상(테이블)별로 묶는다.**

이유:
- 소스가 늘어나도 파일 수가 늘지 않음
- 하나의 스크립트가 하나의 테이블 책임 → 유지보수 명확
- 실행 순서가 파이프라인 1단계(크롤링)와 일치

---

## 스크립트 5개 = 1차 소스 전체 커버

```
scripts/
├── collect_stocks.py    ← 회사 + 시세 + 재무
├── collect_macro.py     ← 거시 지표
├── collect_events.py    ← 이벤트 + 원문
├── collect_energy.py    ← 에너지
└── collect_trade.py     ← 무역 통계
```

---

## 스크립트별 상세

### 1. collect_stocks.py

| 항목 | 내용 |
|---|---|
| 저장 테이블 | `companies`, `financials`, `price_daily`, `consensus` |
| 소스 | yfinance (미국), KRX API (한국 시세), OpenDART (한국 재무), 네이버증권 (컨센서스) |
| API 키 | KRX_API_KEY, DART_API_KEY |

```python
def fetch_us_stocks(tickers):     # yfinance → companies, financials, price_daily
def fetch_kr_prices(tickers):     # KRX API → companies, price_daily
def fetch_kr_financials(tickers): # OpenDART → financials
def fetch_consensus(tickers):     # 네이버증권 → consensus (2차 구축)
```

### 2. collect_macro.py

| 항목 | 내용 |
|---|---|
| 저장 테이블 | `macro_indicators` |
| 소스 | FRED (미국), ECOS (한국), BLS (미국 고용) |
| API 키 | FRED_API_KEY, ECOS_API_KEY, BLS_API_KEY |

```python
def fetch_fred():    # 금리, 환율, 원자재, 물가, 경기, 신용스프레드, 유동성
def fetch_ecos():    # 기준금리, 국고채, 원/달러, 소비자물가, M2
def fetch_bls():     # 고용, 실업, 임금
```

### 3. collect_events.py

| 항목 | 내용 |
|---|---|
| 저장 테이블 | `documents`, `events` |
| 소스 | Google News RSS, OpenDART (공시 목록), SEC EDGAR, 정부 보도자료 |
| API 키 | DART_API_KEY (SEC는 User-Agent만) |

```python
def fetch_news(tickers):          # Google News RSS → documents + events
def fetch_dart_filings(tickers):  # OpenDART 공시검색 → documents + events
def fetch_sec_filings(tickers):   # SEC EDGAR → documents + events
def fetch_policy_releases():      # 금융위/산업부 보도자료 (2차 구축)
```

### 4. collect_energy.py

| 항목 | 내용 |
|---|---|
| 저장 테이블 | `energy` |
| 소스 | EIA Open Data API |
| API 키 | EIA_API_KEY |

```python
def fetch_eia():  # 원유, 가스, 발전, 전력가격, 재고
```

### 5. collect_trade.py

| 항목 | 내용 |
|---|---|
| 저장 테이블 | `trade_stats` |
| 소스 | 관세청 무역통계 API, U.S. Census (장기) |
| API 키 | DATA_GO_KR_API_KEY |

```python
def fetch_customs_kr():    # 관세청 → 국가별 수출입
def fetch_census_trade():  # U.S. Census (2차 구축)
```

---

## 저장 대상 ↔ 스크립트 ↔ 소스 매핑

| raw.db 테이블 | 스크립트 | 소스 | 구축 시기 |
|---|---|---|---|
| `companies` | collect_stocks | yfinance, KRX | 1차 |
| `financials` | collect_stocks | yfinance, OpenDART | 1차 |
| `price_daily` | collect_stocks | yfinance, KRX | 1차 |
| `consensus` | collect_stocks | 네이버증권, FnGuide | 2차 |
| `macro_indicators` | collect_macro | FRED, ECOS, BLS | 1차 |
| `documents` | collect_events | News RSS, DART, SEC | 1차 |
| `events` | collect_events | News RSS, DART, SEC | 1차 |
| `energy` | collect_energy | EIA | 1차 (키 발급 후) |
| `trade_stats` | collect_trade | 관세청 | 1차 |
| `industry_metrics` | (수동/2차) | 협회, 산업 보고서 | 2차 |

---

## 실행 방법

### 전체 크롤링 (매일)
```bash
python scripts/collect_stocks.py
python scripts/collect_macro.py
python scripts/collect_events.py
python scripts/collect_energy.py
python scripts/collect_trade.py
```

### 개별 소스만
```bash
python scripts/collect_macro.py --source fred
python scripts/collect_macro.py --source ecos
python scripts/collect_stocks.py --source yfinance --tickers AAPL,MSFT
```

### 기간 지정
```bash
python scripts/collect_macro.py --days 30      # 최근 30일
python scripts/collect_stocks.py --days 365    # 최근 1년
```

---

## 공통 구조 (모든 스크립트)

```python
"""
collect_xxx.py — {테이블명} 크롤링
"""
import sys
sys.path.insert(0, str(Path(__file__).parent))
from load_env import get_key

DB_PATH = Path(__file__).parent.parent / 'db' / 'raw.db'

def fetch_source_a():
    """소스 A에서 데이터 수집 → raw.db 저장"""
    ...

def fetch_source_b():
    """소스 B에서 데이터 수집 → raw.db 저장"""
    ...

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', default='all')
    parser.add_argument('--days', type=int, default=365)
    args = parser.parse_args()
    
    if args.source in ('all', 'source_a'):
        fetch_source_a()
    if args.source in ('all', 'source_b'):
        fetch_source_b()

if __name__ == '__main__':
    main()
```

---

## 구현 우선순위

| 순서 | 스크립트 | 사용 가능한 소스 | 차단된 소스 |
|---|---|---|---|
| 1 | collect_macro.py | FRED, ECOS, BLS | - |
| 2 | collect_stocks.py | yfinance | KRX (승인 대기) |
| 3 | collect_events.py | Google News, DART, SEC | - |
| 4 | collect_trade.py | 관세청 | - |
| 5 | collect_energy.py | - | EIA (키 미발급) |
