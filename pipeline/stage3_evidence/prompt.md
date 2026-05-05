# Stage 3 — evidence (근거 수집)

> Status: SKELETON (Phase A). 실제 구현은 Phase C.
> Model: Claude Sonnet 4.6 (정리 단계만, 수집 자체는 코드)
> Version: v0.1.0 (placeholder)

## 역할

2단계 픽한 thesis를 뒷받침할 **근거 데이터를 자동 수집**하고 LLM이 정리.

## 입력
- 2단계 픽한 thesis 1개

## 처리 흐름
1. 코드(crawler/)가 외부 API 자동 호출
2. raw 데이터 수집
3. LLM이 thesis 관점에 맞춰 핵심 발췌·요약

## 외부 데이터 소스 (crawler/ 모듈로 wrapper)
- **공시**
  - DART (한국)
  - SEC EDGAR (미국, 미연결)
- **재무·시세**
  - Finnhub
  - Alpha Vantage
  - Polygon
  - yfinance / FinanceDataReader (선택)
- **거시·통계**
  - FRED (미국)
  - ECOS (한국은행)
  - BLS (미국 노동)
  - EIA (미국 에너지)
  - DATA_GO_KR (한국 공공)
- **뉴스**
  - NewsAPI
  - Naver Search

## 출력 형식
JSON 또는 마크다운 dump. 다음 구조:
```yaml
thesis: "..."
ticker: "ORCL"
evidence:
  공시: [...]
  재무: [...]
  컨센: [...]
  거시: [...]
  뉴스: [...]
```

## TODO (Phase C)
- [ ] crawler 모듈별 실제 호출 로직
- [ ] thesis별 자동 query mapping
- [ ] 캐시 전략
