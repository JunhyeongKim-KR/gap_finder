---
description: 1단계 — 글감 후보 3개 생성 (longlist 또는 사용자 지정 종목 기반)
allowed-tools: Bash, Read, Write
argument-hint: "<ticker?>"
---

# /brief

5단계 파이프라인 1단계. longlist 또는 사용자가 지정한 종목·이슈에서 **글감 후보 3개**를 생성.

## 호출 방법
- 직접: `/brief` 또는 `/brief ORCL`
- 자연어 트리거: "글감 뽑아", "글감 후보", "주제 후보", "이번주 글감"

## 입력
- `data/candidates/longlist_<latest>.json` (있으면)
- 또는 인자로 받은 ticker
- 또는 사용자가 던진 종목·이슈

## 작업
1. `pipeline/stage1_brief/prompt.md` 의 prompt 로드
2. `pipeline/shared/philosophy.md` 와 `writing_principles.md` 참조
3. Sonnet 4.6 호출 → 글감 후보 3개 생성
4. 출력 형식:
   - [A] 종목 분석 — ...
   - [B] 산업 구조 — ...
   - [C] 통념 비판 — ...
5. CEO 픽 + 코멘트 입력 대기

## 다음 단계
CEO 픽 시 `/angle <ticker>` 자동 호출. 픽·코멘트는 `data/picks/`에 자동 기록.

## 현재 상태
Phase A skeleton — `runners/pipeline.py --stage brief` 호출 시 NotImplementedError. Phase B/C 이후 동작.
