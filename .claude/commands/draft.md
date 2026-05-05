---
description: 4단계 — 본문 초안 작성 (Sonnet 4.6, 글의 기본 문법 준수)
allowed-tools: Bash, Read, Write
argument-hint: "<ticker>"
---

# /draft

5단계 파이프라인 4단계. 1+2+3단계 누적 정보로 본문 초안 작성.

## 호출 방법
- 직접: `/draft ORCL`
- 자연어 트리거: "초안 써", "본문 작성", "글 써"

## 입력
- 1단계 글감
- 2단계 thesis (+ CEO 코멘트)
- 3단계 evidence

## 작업
1. `pipeline/stage4_draft/prompt.md` 의 prompt 로드
2. `pipeline/shared/writing_principles.md` 의 표준 섹션 적용
3. Sonnet 4.6 호출
4. 본문 마크다운 생성 → `data/articles/<ticker>_<YYYYMMDD>_draft.md`

## 글의 기본 문법
`[시장 컨센서스] → [해석의 맹점] → [실제 메커니즘] → [진짜 수혜/피해] → [체크포인트]`

## CEO 검수
4단계 후 CEO가 1차 검수. "OK" 또는 "수정 [코멘트]". 5단계는 명시적 OK 후에만 진입.

## 다음 단계
CEO "OK" → `/polish <ticker>`. 수정 요청 → 재생성.

## 현재 상태
Phase A skeleton — Phase C 이후 동작.
