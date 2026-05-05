---
description: 2단계 ⭐ — 시장 view 반박 thesis 후보 3개 생성 (Opus 4.7)
allowed-tools: Bash, Read, Write
argument-hint: "<ticker>"
---

# /angle ⭐

5단계 파이프라인 **2단계** — 본 시스템의 가장 중요한 단계. 시장이 보는 view를 반박하는 thesis 후보 3개 생성.

## 호출 방법
- 직접: `/angle ORCL`
- 자연어 트리거: "thesis 뽑아", "분석 관점", "각도 잡아", "ORCL thesis"

## 모델
**Claude Opus 4.7** — 5단계 중 유일하게 Opus 사용 (차별화 핵심).

## 입력
- 1단계에서 픽한 글감 (또는 직접 ticker)
- 컨센 요약 (한경 컨센서스 등)
- (선택) CEO 코멘트

## 작업
1. `pipeline/stage2_angle/prompt.md` 의 prompt 로드
2. `pipeline/shared/philosophy.md` 와 `writing_principles.md` 참조
3. Opus 4.7 호출 → thesis 후보 3개 생성
4. 각 thesis마다:
   - 핵심 한 줄
   - 근거 (3~5문장)
   - novelty (1~10), defensibility (1~10) 자가 평가
5. judge 자동 채점 (`pipeline/judge/prompt.md`)
6. overall < 6점 시 자동 reject + 재생성

## 절대 금지
- 단순 가격 추세, 기술적 분석, "좋은 회사인가" 류 가치 판단

## 다음 단계
CEO 픽 + 코멘트 → `/evidence <ticker>` 자동 호출.

## 현재 상태
Phase A skeleton — Phase B 최우선 검증 대상. eval set 5개(오라클·에코프로·SK하이닉스·삼바·TSMC)로 시연 후 CEO go/no-go.
