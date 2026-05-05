# Judge — LLM-as-judge 자동 평가

> Status: SKELETON (Phase A). 실제 prompt 내용은 Phase B.
> Model: Claude Sonnet 4.6
> Version: v0.1.0 (placeholder)

## 역할

각 단계의 산출물을 자동 채점. 6점 미만이면 자동 reject + 재생성.

## 평가 항목 (1~10점)

### 2단계 (angle) — thesis 평가
- `novelty` — 시장에서 드물게 다루는 정도
- `defensibility` — 데이터로 방어 가능한 정도
- `contrarian_strength` — 시장 view 반박의 명확성
- `tone_consistency` — 글쓰기 원칙 부합도

### 4단계 (draft) — 본문 평가
- `fact_check` — 숫자·인용 출처 명시
- `thesis_clarity` — thesis가 본문에서 명확히 드러나는가
- `framework_adherence` — `[컨센서스]→[맹점]→[메커니즘]→[수혜/피해]→[체크포인트]` 구조
- `tone_consistency`

### 5단계 (polish) — 후킹 평가
- `hook_strength` — CTR 예상치
- `non_clickbait` — 어그로화 회피
- `title_clarity`

## 출력 형식
```yaml
stage: stage2_angle
overall: 7.4
scores:
  novelty: 8
  defensibility: 7
  contrarian_strength: 7
  tone_consistency: 8
verdict: pass    # pass | reject
notes: |
  thesis 1번은 OCI 회계 인식 차이를 명확히 잡아냄.
  thesis 3번은 peer group 정의가 모호함.
```

## TODO (Phase B)
- [ ] 단계별 평가 항목·prompt 확정
- [ ] reject 시 재생성 flow
