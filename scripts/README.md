# scripts — 자동화 스크립트

## API 키 설정

크롤링 스크립트를 실행하려면 API 키가 필요합니다.

### 빠른 설정

```bash
python scripts/setup_keys.py
```

대화형으로 각 소스의 API 키를 입력받아 `.env` 파일에 저장합니다.

### 수동 설정

프로젝트 루트에 `.env` 파일을 만들고 키를 입력:

```
FRED_API_KEY=your_key_here
ECOS_API_KEY=your_key_here
DART_API_KEY=your_key_here
EIA_API_KEY=your_key_here
BLS_API_KEY=your_key_here
KRX_API_KEY=your_key_here
DATA_GO_KR_API_KEY=your_key_here
```

### API 키 발급처

| 소스 | 용도 | 발급 URL | 비용 |
|---|---|---|---|
| FRED | 미국 거시 (금리/물가/고용) | https://fred.stlouisfed.org/docs/api/api_key.html | 무료 |
| ECOS | 한국은행 (금리/환율/물가) | https://ecos.bok.or.kr/api/#/AuthKeyApply | 무료 |
| OpenDART | 한국 공시/재무제표 | https://opendart.fss.or.kr | 무료 |
| EIA | 미국 에너지 (원유/가스/전력) | https://www.eia.gov/opendata/register.php | 무료 |
| BLS | 미국 고용/임금/물가 | https://data.bls.gov/registrationEngine/ | 무료 |
| KRX | 한국거래소 시세 | https://data.krx.co.kr | 무료 |
| 관세청 | 무역통계 | https://data.go.kr | 무료 |

### 보안

- `.env` 파일은 `.gitignore`에 포함되어 **git에 올라가지 않습니다**
- API 키를 코드에 직접 넣지 마세요
- 크롤러에서 키를 사용할 때: `from load_env import get_key`

## 스크립트 목록

### DB 초기화
| 스크립트 | 역할 |
|---|---|
| `init_raw_db.py` | raw.db 생성 (1~2층: 원문+정형) |
| `init_enriched_db.py` | enriched.db 생성 (3층: 해석) |

### 크롤러 (1차 소스)
| 스크립트 | 소스 | 저장 테이블 | API 키 |
|---|---|---|---|
| `collect_us.py` | yfinance | companies, financials, price_daily | 불필요 |
| `collect_fred.py` | FRED API | macro_indicators | FRED_API_KEY |
| `collect_ecos.py` | ECOS API | macro_indicators | ECOS_API_KEY |
| `collect_news.py` | Google News RSS | documents, events | 불필요 |
| `collect_macro.py` | FRED (기존) | raw/macro/ JSON | FRED_API_KEY |

### 유틸리티
| 스크립트 | 역할 |
|---|---|
| `load_env.py` | .env에서 API 키 로드 |
| `setup_keys.py` | 대화형 키 설정 |

### Deprecated
| 스크립트 | 대체 |
|---|---|
| `init_db.py` | → `init_raw_db.py` + `init_enriched_db.py` |
| `seed_nike.py` | → 크롤러로 대체 |
