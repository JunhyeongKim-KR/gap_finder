# agents/crawler — 1단계 크롤링

## 스크립트 목록

### 크롤러 (5개)
| 스크립트 | 소스 | 저장 테이블 |
|---|---|---|
| collect_stocks.py | yfinance + DART + KRX | companies, financials, price_daily |
| collect_macro.py | FRED + ECOS + BLS | macro_indicators |
| collect_events.py | News + DART공시 + SEC | documents, events |
| collect_energy.py | EIA | energy |
| collect_trade.py | 관세청 | trade_stats |

### DB 초기화
| 스크립트 | 역할 |
|---|---|
| init_raw_db.py | raw.db 생성 (1~2층) |
| init_enriched_db.py | enriched.db 생성 (3층) |

### 유틸리티
| 스크립트 | 역할 |
|---|---|
| load_env.py | .env에서 API 키 로드 |
| setup_keys.py | 대화형 키 설정 |

## API 키 설정

```bash
python agents/crawler/setup_keys.py
```

또는 프로젝트 루트에 `.env` 파일 직접 편집.

## 실행

```bash
python run.py crawl              # 전체 크롤링
python run.py crawl --source stocks  # 종목만
```
