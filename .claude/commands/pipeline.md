---
description: 1~5단계 chain 한번에 (CEO 픽 멈춤 포함)
allowed-tools: Bash, Read, Write
argument-hint: "<ticker>"
---

# /pipeline

5단계 chain을 처음부터 끝까지 자동 진행. 단, CEO 픽 지점(1·2·4·5)에서는 멈춰서 사용자 입력 대기.

## 호출 방법
- 직접: `/pipeline ORCL`
- 자연어 트리거: "처음부터 끝까지", "글 1편 만들어", "ORCL 글 써줘"

## 흐름
```
/brief ORCL → CEO 픽 대기
            ↓ (픽 시 자동 진행)
/angle ORCL → CEO 픽 대기
            ↓
/evidence ORCL → 자동
            ↓
/draft ORCL → CEO 검수 대기
            ↓ (OK 시)
/polish ORCL → CEO 후킹 픽 대기
            ↓
/publish ORCL → 발행
```

## 실행
`runners/pipeline.py --stage all --ticker <ticker>` 호출.

## 현재 상태
Phase A skeleton. Phase B 이후 단일 단계부터 구동, Phase C 이후 chain 전체 동작.
