# Stage 1 — brief (글감 잡기)

> Status: SKELETON (Phase A). 실제 prompt 내용은 Phase B 이후 작성.
> Model: Claude Sonnet 4.6
> Version: v0.1.0 (placeholder)

## 역할

longlist 또는 사용자 input에서 **글감 후보 3개**를 분류·정리하여 제시.

## 입력
- `longlist` (15개 후보) 또는 사용자가 직접 지정한 종목·이슈
- (선택) 사용자 코멘트

## 출력 형식
3개 후보를 카테고리로 분류:
- [A] 종목 분석 — 특정 종목의 시장 view 반박
- [B] 산업 구조 — 특정 산업의 변화·재편
- [C] 통념 비판 — 시장에서 통용되는 지표·해석의 함정

각 후보에 1줄 요약 첨부.

## 작성 원칙
- `pipeline/shared/philosophy.md` 참조
- `pipeline/shared/writing_principles.md` 참조

## TODO (Phase B 이후)
- [ ] 실제 prompt body 작성
- [ ] eval set 5개 작성
