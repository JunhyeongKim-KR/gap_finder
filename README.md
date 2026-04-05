# GapFinder

**역발상 투자 리서치 콘텐츠 시스템**

시장 기대와 실제 사업가치의 괴리를 찾아내, DB 기반으로 분석 콘텐츠를 반복 생산하는 반자동 운영 체계.

> **[Live 대시보드](https://junhyeongkim-kr.github.io/gap_finder/viz/index.html)** — 브라우저에서 바로 확인

---

## 4단계 파이프라인

### 1단계: raw DB 크롤링 `토큰 X`

```
인터넷 데이터  →  크롤링 스크립트  →  raw DB
                  scripts/collect_*.py    날것 숫자/뉴스 저장
```

### 2단계: DB 구축 (재해석) `토큰 O`

```
raw DB + 철학.md  →  재해석 Agent  →  재해석 DB
                     docs/12 적용       맥락/비교/프레임 해석 포함
```

| raw DB (날것) | → 재해석 후 | 왜 필요? |
|---|---|---|
| 매출 74조 | 전분기 +8%, 컨센서스 -2% | 비교/맥락 부여 |
| PER 12.5 | 5년 밴드 하단 20% | 밸류에이션 맥락화 |
| HBM3E 뉴스 5건 | 자본사이클형 프레임 → 공급 축소 판단 | 철학 프레임 적용 |

### 3단계: 글쓰기 `토큰 O`

```
재해석 DB + 글쓰기.md + 템플릿.md  →  글쓰기 Agent  →  글 초안  →  CEO 검수
             docs/13 + docs/07                         output/TICKER_종목명.md
```

### 4단계: 배포 `토큰 X`

```
검수된 글  →  배포 스크립트  →  티스토리 (원문) + 네이버 (축약)
```

### 토큰 비용 요약

| 단계 | 토큰 | 이유 |
|---|---|---|
| 1. raw DB 크롤링 | X | 스크립트가 API 호출만 |
| 2. DB 구축 (재해석) | **O** | Agent가 데이터를 읽고 철학 프레임으로 해석 |
| 3. 글쓰기 | **O** | Agent가 재해석 DB + 글쓰기 원칙으로 글 생성 |
| 4. 배포 | X | 스크립트가 복붙만 |

**글의 기본 문법:** `[시장 컨센서스]` → `[해석의 맹점]` → `[실제 메커니즘]` → `[진짜 수혜/피해]` → `[체크포인트]`

---

## 팀 구성

| 역할 | 담당 | 하는 일 |
|---|---|---|
| **CEO** | 기획·판단·콘텐츠 방향 | 종목 선정, 분석 결론 검수, 글 품질 판단 |
| **CTO** | 개발·자동화·시스템 | DB 설계, 크롤링, 자동화, 코드 |
| **Claude** | 보조 | 글 초안 생성, DB 조회, 문서 작성 |

---

## 현재 상태

| 항목 | 상태 |
|---|---|
| Phase | **0 완료** → Phase 1 진행 예정 |
| 커버리지 | 삼성전자 (005930.KS) + 나이키 (NKE) |
| DB | SQLite 5테이블 (3테이블 확장 예정) |
| Agent 프롬프트 | 22개 투자 철학 + 10대 글쓰기 원칙 |
| 스크립트 | 5종 (init, seed, collect_us, collect_news, collect_macro) |
| 플랫폼 | 한국(네이버+티스토리) 먼저 → 워드프레스 영어권 |

---

## 폴더 구조

```
gap_finder/
│
├── board/                  ← CEO·CTO 소통 공간
│   ├── requests/           ← 요청사항 (CEO → CTO)
│   ├── decisions/          ← 확정된 결정사항
│   └── reviews/            ← 글 리뷰·피드백
│
├── docs/                   ← 전략 문서 (사업 설계도)
│   ├── 01  사업성 평가
│   ├── 02  플랫폼 전략
│   ├── 04  DB 설계 (8테이블, A~J 데이터 범주)
│   ├── 05  매크로 업데이트 체계
│   ├── 06  로드맵 (Phase 0~4)
│   ├── 07  글 템플릿 (9섹션)
│   ├── 09  체크리스트
│   ├── 10  데이터 파이프라인 (크롤링 2종)
│   ├── 12  투자 철학 프레임 (22개)  ← 핵심
│   └── 13  글쓰기 원칙 (10대 원칙)  ← 핵심
│
├── status/                 ← 프로젝트 현황판
│   ├── progress.md         ← 전체 진행 상황
│   ├── coverage.md         ← 종목 커버리지 현황
│   └── changelog.md        ← 변경 이력
│
├── output/                 ← 생성된 종목 분석글
│   ├── 005930_삼성전자_20260401.md
│   └── NKE_나이키_20260401_naver.md
│
├── db/                     ← SQLite 데이터베이스
│   └── gapfinder.db
│
├── scripts/                ← 자동화 스크립트
│   ├── init_db.py          ← DB 초기화 + 삼성전자 샘플
│   ├── seed_nike.py        ← 나이키 데이터
│   ├── collect_us.py       ← yfinance 미국주식 수집
│   ├── collect_news.py     ← Google News RSS
│   └── collect_macro.py    ← FRED 매크로 지표
│
└── viz/                    ← 시각화 대시보드
    ├── index.html          ← 메인 대시보드 (9탭)
    └── example_workflow.html
```

---

## 핵심 문서

| 문서 | 설명 |
|---|---|
| [투자 철학 프레임](docs/12_investment_philosophy.md) | 22개 해석 프레임워크 — Agent의 사고방식 |
| [글쓰기 원칙](docs/13_writing_principles.md) | 블로그 정체성, 기본 문법, 10대 원칙 |
| [DB 설계](docs/04_database_design.md) | 8테이블 + CEO A~J 데이터 범주 매핑 |
| [데이터 파이프라인](docs/10_data_pipeline.md) | 크롤링 2종, 스크립트 5종, 워크플로우 |
| [글 템플릿](docs/07_article_template.md) | 종목 분석글 9섹션 표준 구조 |
| [재해석 Agent 가이드](docs/14_agent_reinterpret.md) | 2단계 Agent — raw DB → 철학 적용 → 재해석 DB |
| [글쓰기 Agent 가이드](docs/15_agent_writer.md) | 3단계 Agent — 재해석 DB → 분석글 초안 |
| [로드맵](docs/06_roadmap.md) | Phase 0~4 단계별 계획 |

전체 문서 목록: [docs/README.md](docs/README.md)

---

## CEO 사용법

이 폴더에서 Claude를 열고 자연어로 말하면 됩니다.

```
"삼성전자 분석 글 만들어줘"          → output/ 에 분석글 생성
"현재 커버 종목 알려줘"              → status/coverage.md 안내
"요청 남길게 — SK하이닉스 추가해줘"  → board/requests/ 에 기록
"이번 주 진행 상황"                  → status/progress.md 요약
```

코드, DB, Git 관련은 모두 CTO가 처리합니다.

---

## 핵심 원칙

1. 신규 장문 남발 금지 — **DB 재활용 + 업데이트 반복**이 수익 구조
2. 모든 글은 **DB에서 출발** — 글 먼저 쓰고 정리하는 방식 금지
3. 자동화는 재가공부터 — **목표주가·결론은 자동화 금지**
4. 사람은 판단만 한다 — 데이터 정리·초안·재가공은 기계
5. 유료는 병목에만 쓴다 — '편해 보여서' 결제 금지
