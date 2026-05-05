# Stage 2 — angle (분석 관점) ⭐

> Status: SKELETON (Phase A). 실제 prompt 내용은 **Phase B 최우선 검증 대상.**
> Model: **Claude Opus 4.7** (5단계 중 유일하게 Opus 사용)
> Version: v0.1.0 (placeholder)

## 역할

시장이 보는 view를 **반박**하는 thesis 후보 3개를 생성. 본 시스템의 가장 중요한 단계.

## 입력
- 1단계 픽한 글감 (1개)
- 컨센 요약 (한경 컨센서스, 애널리스트 리포트 등)
- (선택) CEO 코멘트

## 출력 형식
thesis 후보 3개. 각 thesis마다:
- 핵심 한 줄
- 근거 (3~5문장)
- novelty (1~10) — 시장에서 드물게 다루는 정도
- defensibility (1~10) — 데이터로 방어 가능한 정도

## 절대 금지
- 단순 가격 추세
- 기술적 분석
- "좋은 회사인가" 류의 가치 판단

## 추구해야 할 관점
- 회계 인식 시점 차이
- 재무 이상치 (RPO·deferred revenue·재고 등)
- peer group 정의 자체의 결함
- capex 회수율·자본 재배치 사이클
- 규제·정책 해석 차이

## 평가 기준 (judge가 사용)
- novelty_score_min: 7
- defensibility_score_min: 7
- thesis_count: 3

## TODO (Phase B)
- [ ] 실제 prompt body 작성 (가장 중요)
- [ ] eval set 5개: 오라클·에코프로·SK하이닉스·삼바·TSMC
- [ ] 5종목 시연 → CEO go/no-go 결정
