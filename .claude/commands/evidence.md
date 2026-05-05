---
description: 3단계 — 외부 API 자동 근거 수집 (DART/Finnhub/FRED 등)
allowed-tools: Bash, Read, Write
argument-hint: "<ticker>"
---

# /evidence

5단계 파이프라인 3단계. 2단계 픽한 thesis를 뒷받침할 데이터를 외부 API로 자동 수집.

## 호출 방법
- 직접: `/evidence ORCL`
- 자연어 트리거: "근거 수집", "데이터 모아", "공시·재무 가져와"

## 입력
- 2단계 픽한 thesis 1개

## 외부 데이터 소스 (`crawler/`)
- **공시**: DART (한국)
- **시세·재무**: Finnhub, Alpha Vantage, Polygon
- **거시·통계**: FRED, ECOS, BLS, EIA, DATA_GO_KR
- **뉴스**: NewsAPI, Naver Search

## 작업
1. thesis에서 키워드·메트릭 추출
2. 관련 crawler 모듈 호출
3. raw 데이터 dump → `data/evidence/<ticker>_<YYYYMMDD>/`
4. Sonnet 4.6이 thesis 관점에 맞춰 핵심 발췌·요약

## CEO 개입
없음. 완전 자동.

## 다음 단계
완료 후 `/draft <ticker>` 자동 호출.

## 현재 상태
Phase A skeleton — crawler/ 모듈은 wrapper만, 실제 호출 로직은 Phase C.
