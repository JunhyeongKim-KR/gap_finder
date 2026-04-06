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
├── agents/                 ← AI Agent 전용 프롬프트
│   ├── reinterpret/        ← 2단계: 재해석 Agent
│   │   ├── PROMPT.md       ← 역할, 규칙, 입출력
│   │   └── philosophy.md   ← 투자 철학 22개 프레임
│   └── writer/             ← 3단계: 글쓰기 Agent
│       ├── PROMPT.md       ← 역할, 규칙, 입출력
│       └── writing.md      ← 글쓰기 원칙 12개 + 4패턴
│
├── docs/                   ← 전략 문서 (원본 보관)
│   ├── 01  사업성 평가
│   ├── 02  플랫폼 전략
│   ├── 04  DB 설계 (8테이블, A~J 데이터 범주)
│   ├── 05  매크로 업데이트 체계
│   ├── 06  로드맵 (Phase 0~4)
│   ├── 07  글 템플릿 (참조용)
│   ├── 09  체크리스트
│   ├── 10  데이터 파이프라인
│   ├── 12  투자 철학 프레임 (원본)
│   ├── 13  글쓰기 원칙 (원본)
│   └── 16  크롤링 스크립트 구조
│
├── output/                 ← 생성된 분석글
│
├── db/                     ← SQLite 데이터베이스
│   ├── raw.db              ← 1~2층: 원문 + 정형 데이터
│   └── enriched.db         ← 3층: 해석/지식
│
├── scripts/                ← 자동화 스크립트
│   ├── collect_stocks.py   ← yfinance + DART + KRX
│   ├── collect_macro.py    ← FRED + ECOS + BLS
│   ├── collect_events.py   ← News + DART공시 + SEC
│   ├── collect_energy.py   ← EIA
│   ├── collect_trade.py    ← 관세청
│   ├── init_raw_db.py      ← raw.db 초기화
│   ├── init_enriched_db.py ← enriched.db 초기화
│   └── setup_keys.py       ← API 키 설정
│
├── run.py                  ← 파이프라인 실행기
│
└── viz/                    ← 시각화 대시보드
    ├── index.html          ← 메인 대시보드 (5탭)
    └── example_workflow.html
```

---

## 핵심 문서

### Agent (최적화된 최신 전략)
| 폴더 | 설명 |
|---|---|
| [agents/reinterpret/](agents/reinterpret/) | 2단계 — raw DB + 철학 → enriched DB |
| [agents/writer/](agents/writer/) | 3단계 — enriched DB → 칼럼형 분석글 |

### 콘텐츠 규격 (원본)
| 문서 | 설명 |
|---|---|
| [투자 철학 프레임](docs/12_investment_philosophy.md) | 22개 해석 프레임워크 |
| [글쓰기 원칙](docs/13_writing_principles.md) | 12대 원칙 + 4패턴 |

### DB
| 문서 | 설명 |
|---|---|
| [DB 설계](docs/04_database_design.md) | 8테이블 + A~J 데이터 범주 매핑 |
| [데이터 파이프라인](docs/10_data_pipeline.md) | 크롤링 2종, 스크립트 5종 |

### 운영
| 문서 | 설명 |
|---|---|
| [로드맵](docs/06_roadmap.md) | Phase 0~4 계획 |
| [매크로 업데이트](docs/05_macro_update_system.md) | 이슈 발생 시 처리 규칙 |
| [체크리스트](docs/09_checklist.md) | 발행 전 확인 항목 |

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
