---
description: 5단계 — 팩트체크 + 후킹 강도 변형 3개 (강·중·약)
allowed-tools: Bash, Read, Write
argument-hint: "<ticker>"
---

# /polish

5단계 파이프라인 5단계. 4단계 초안을 팩트체크하고 제목·후킹 변형 3개 생성.

## 호출 방법
- 직접: `/polish ORCL`
- 자연어 트리거: "다듬어", "팩트체크", "제목 뽑아", "후킹"

## 작업
1. `pipeline/stage5_polish/prompt.md` 의 prompt 로드
2. Sonnet 4.6 호출
3. 출력:
   - 팩트체크 결과 (출처 누락·검증 필요 항목)
   - 후킹 강도 3변형:
     - **[A] 강함** — 반박조 ("거짓말이다" 류)
     - **[B] 중간** — 환기조 ("진짜 문제는 다른 곳" 류)
     - **[C] 약함** — 제시조 ("다른 시각" 류)

## 절대 금지
- 자극적 어그로 제목
- 투자 권유 표현

## CEO 픽
강·중·약 중 1개 선택.

## 다음 단계
CEO 픽 → `/publish <ticker>` 자동 호출 (또는 사용자 명시 호출).

## 현재 상태
Phase A skeleton.
