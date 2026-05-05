# GapFinder

역발상 투자 리서치 콘텐츠 시스템 — 5단계 자동화 파이프라인.

## 5분 요약

시장 통념을 한 단계 더 의심하는 분석 블로그를 5단계 자동화로 운영. CEO는 1편당 5~10분만 투입(글감·thesis·후킹 픽).

상세 시스템 구조: [`ARCH.md`](./ARCH.md)
협업 가이드: [`CLAUDE.md`](./CLAUDE.md)

## Quickstart

```bash
# 1. .env 작성 (.env.example 참조)
cp .env.example .env
# 편집: ANTHROPIC_API_KEY 외 11종 키 입력 (대부분 이미 .env에 있음)

# 2. 의존성 설치
pip install -e .
# 또는: pip install -e ".[data,dev]"

# 3. 단계별 실행 (Phase B 이후 동작)
python runners/pipeline.py --stage angle --ticker ORCL
python runners/longlist.py
python runners/eval_runner.py --stage angle
```

## Claude Code 워크플로우

본 시스템은 Claude Code 터미널에서 **슬래시 커맨드 + 자연어**로 운영.

```
/longlist                 매주 월요일 후보 15개
/brief <ticker?>          1단계 글감 후보 3개
/angle <ticker>           2단계 thesis 3개 ⭐ Opus 4.7
/evidence <ticker>        3단계 자동 근거 수집
/draft <ticker>           4단계 본문 초안
/polish <ticker>          5단계 팩트체크 + 후킹 3개
/pipeline <ticker>        1~5 chain (CEO 픽 멈춤)
/publish <ticker>         티스토리 발행
/eval <stage>             평가셋 자동 채점
```

자연어로도 호출 가능 — 예: "오라클 thesis 뽑아줘" → `/angle ORCL`. 매핑은 [`CLAUDE.md`](./CLAUDE.md) 참조.

## 폴더 구조

```
gap_finder/
├── ARCH.md                      5단계 시스템 구조 (mermaid)
├── CLAUDE.md                    Claude 가이드
├── pipeline/                    5단계 prompt + judge + shared
│   ├── stage1_brief/
│   ├── stage2_angle/            ⭐ Phase B 최우선
│   ├── stage3_evidence/
│   ├── stage4_draft/
│   ├── stage5_polish/
│   ├── judge/
│   └── shared/                  philosophy + writing_principles
├── runners/                     실행 스크립트
│   ├── pipeline.py
│   ├── longlist.py
│   └── eval_runner.py
├── crawler/                     외부 API wrapper 11종
├── data/                        런타임 산출 (gitignore 일부)
│   ├── articles/  candidates/  evidence/
├── .claude/commands/            슬래시 커맨드 9종
├── infra/langfuse/              LLMOps (Phase A 후반)
├── board/                       CEO/CTO 협업 기록
└── v0.1/                        legacy 격리
```

## 현재 상태

**Phase A 진행 중** (2026-05-05 시작). 폴더·skeleton·슬래시 커맨드 구축 단계. 실제 prompt body와 LLM 호출 로직은 Phase B 이후 채워짐.

다음 마일스톤: **Phase B — 2단계 (angle) prompt 검증** (오라클·에코프로·SK하이닉스·삼바·TSMC eval 5종 시연 → CEO go/no-go).
