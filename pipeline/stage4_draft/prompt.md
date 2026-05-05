# Stage 4 — draft (본문 작성)

> Status: SKELETON (Phase A). 실제 prompt 내용은 Phase C.
> Model: Claude Sonnet 4.6
> Version: v0.1.0 (placeholder)

## 역할

1+2+3단계 누적 정보로 **본문 초안**을 작성.

## 입력
- 1단계 글감
- 2단계 thesis (+ CEO 코멘트)
- 3단계 evidence

## 출력 형식
마크다운 본문. 글의 기본 문법 준수:

`[시장 컨센서스] → [해석의 맹점] → [실제 메커니즘] → [진짜 수혜/피해] → [체크포인트]`

## 작성 원칙 (반드시 준수)
1. 확인되지 않은 수치는 단정 금지
2. 공식 자료 확인 시에만 숫자 제시
3. 불확실하면 "확인되지 않으나…", "가설적 추론 전제" 표현
4. 사실·해석·추론 구분
5. 목표주가는 시나리오와 가정에 따라 제시
6. 철회조건은 '가격'이 아니라 '가설 붕괴 조건'

세부: `pipeline/shared/writing_principles.md`

## CEO 검수
4단계 후 CEO가 1차 검수. "OK" 또는 "수정 [코멘트]". 5단계는 CEO 명시 OK 후 진입.

## TODO (Phase C)
- [ ] 실제 prompt body 작성
- [ ] eval set 5개
