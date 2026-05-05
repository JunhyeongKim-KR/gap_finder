---
description: 단계별 평가셋으로 LLM-as-judge 품질 검증
allowed-tools: Bash, Read
argument-hint: "<stage> <sample?>"
---

# /eval

단계별 prompt 품질을 LLM-as-judge로 자동 평가.

## 호출 방법
- 직접: `/eval angle` (전체) / `/eval angle sample_001.yaml` (단건)
- 자연어 트리거: "평가 돌려", "judge 시켜", "stage2 검증"

## 작업
1. `runners/eval_runner.py --stage <stage> [--sample <name>]` 실행
2. `pipeline/<stage_folder>/eval/*.yaml` 의 정답셋 로드
3. 각 sample에 대해 단계 prompt 호출 → judge prompt 채점
4. 결과: `data/traces/eval_<stage>_<YYYYMMDD>.json`

## 단계 옵션
- `brief` / `angle` / `evidence` / `draft` / `polish`

## Phase B 우선 사용
2단계(angle) eval 5개로 시연 → CEO go/no-go 판단의 근거.

## 현재 상태
Phase A skeleton — eval set과 judge prompt 모두 placeholder. Phase B에서 stage2_angle eval 5개 작성 시 즉시 사용 가능.
