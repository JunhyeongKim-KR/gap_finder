# GapFinder — 5단계 시스템 구조

> 작성일: 2026-05-05
> 목적: CEO·CTO·Claude 공통 멘탈 모델 정렬용 시각 자료
>
> **5단계 파이프라인 정의 출처:**
> - CEO 방향성 원문: [`board/requests/20260505_블로그운영시스템_보고서.md`](./board/requests/20260505_블로그운영시스템_보고서.md)
> - CTO 액션플랜: [`board/docs/20260505_CTO_액션플랜_v2.md`](./board/docs/20260505_CTO_액션플랜_v2.md)

---

## 1. 전체 시스템 흐름

```mermaid
flowchart TD
    %% 외부 소스
    Universe[("외부 소스<br/>KOSPI200 + KOSDAQ150 + S&P500")]
    PublicData[("외부 데이터<br/>DART · SEC · yfinance<br/>KRX · 네이버뉴스 · Reuters")]
    Consensus[("외부 데이터<br/>한경 컨센서스")]
    Tistory[("발행<br/>티스토리")]

    %% 사전 단계
    L["/longlist<br/>매주 월요일 자동"]
    Universe -->|"850종목"| L

    %% 1단계
    S1["①단계: brief<br/>글감 잡기<br/>(Sonnet 4.6)"]
    L -->|"후보 15개"| S1
    CEO1{{"CEO 픽 + 코멘트"}}
    S1 -->|"글감 후보 3개"| CEO1

    %% 2단계
    S2["②단계: angle ⭐<br/>분석 관점<br/>(Opus 4.7)"]
    CEO1 -->|"픽한 글감 1개<br/>+ CEO 코멘트"| S2
    Consensus -->|"컨센 요약"| S2
    CEO2{{"CEO 픽 + 코멘트"}}
    S2 -->|"thesis 후보 3개"| CEO2

    %% 3단계
    S3["③단계: evidence<br/>근거 수집<br/>(자동·LLM 최소)"]
    CEO2 -->|"픽한 thesis 1개"| S3
    PublicData -->|"공시·재무·뉴스 raw"| S3

    %% 4단계
    S4["④단계: draft<br/>본문 작성<br/>(Sonnet 4.6)"]
    S3 -->|"수집된 evidence"| S4
    CEO2 -.->|"thesis + 코멘트"| S4
    CEO4{{"CEO 1차 검수"}}
    S4 -->|"본문 초안"| CEO4

    %% 5단계
    S5["⑤단계: polish<br/>다듬기 + 후킹<br/>(Sonnet 4.6)"]
    CEO4 -->|"검수 통과 초안"| S5
    CEO5{{"CEO 후킹 픽"}}
    S5 -->|"팩트체크 + 후킹 강·중·약"| CEO5

    %% 발행
    P["/publish"]
    CEO5 -->|"최종 글"| P
    P -->|"자동 발행"| Tistory

    %% 사이드 시스템
    OpsDB[("운영 DB<br/>CEO 픽 누적")]
    Judge["judge<br/>LLM-as-judge<br/>품질 자동 평가"]

    CEO1 -.->|"픽·코멘트"| OpsDB
    CEO2 -.->|"픽·코멘트"| OpsDB
    CEO5 -.->|"후킹 픽"| OpsDB

    S2 -.->|"thesis 채점"| Judge
    S4 -.->|"본문 채점"| Judge
    Judge -.->|"6점 미만 reject"| S2

    classDef stage fill:#4a90e2,stroke:#2e5e8e,color:#fff
    classDef ceo fill:#f5a623,stroke:#a8741a,color:#000
    classDef external fill:#7ed321,stroke:#5a9b18,color:#000
    classDef storage fill:#bd10e0,stroke:#7d0a96,color:#fff
    classDef side fill:#9b9b9b,stroke:#666,color:#fff

    class S1,S2,S3,S4,S5,L,P stage
    class CEO1,CEO2,CEO4,CEO5 ceo
    class Universe,Consensus,PublicData,Tistory external
    class OpsDB storage
    class Judge side
```

**색깔 의미**
- 🟦 파랑 = 시스템 단계 (자동 처리)
- 🟧 주황 = CEO 결정 지점 (사람 개입)
- 🟩 초록 = 외부 데이터/발행 채널
- 🟪 보라 = 데이터 저장
- ⚪ 회색 = 사이드 시스템 (자동 평가)

---

## 2. 각 단계 Input/Output 표

| 단계 | Input | 처리 | Output |
|------|-------|------|--------|
| **/longlist** (사전) | universe 850종목, 5개 trigger 필터 (가격·EPS·뉴스·재무이상치 등) | 자동 산출 | **후보 15개 리스트** |
| **①brief** (글감) | longlist 15개 + (선택) CEO 직접 input | LLM 분류·정리 (Sonnet 4.6) | **글감 후보 3개**<br/>(종목 분석/산업 구조/통념 비판) |
| **②angle** ⭐ | ①의 픽 1개 + CEO 코멘트 + 컨센 요약 | **시장 view 반박** thesis 생성 (Opus 4.7) | **thesis 후보 3개** |
| **③evidence** | ②의 픽 1개 (thesis) | 외부 API 자동 호출 (DART/yfinance/뉴스 등) | **수집 데이터 묶음** (공시·재무·뉴스·컨센) |
| **④draft** | ①+②+③ 누적 | LLM 본문 작성 (Sonnet 4.6) | **본문 초안** (마크다운) |
| **⑤polish** | ④의 초안 | 팩트체크 + 후킹 변형 (Sonnet 4.6) | **팩트체크 결과** + **후킹 강·중·약 3개** |
| **/publish** | ⑤의 픽 | 티스토리 OAuth | 발행된 글 (URL) |

---

## 3. CEO가 1편당 마주치는 결정 포인트 4개

```mermaid
flowchart LR
    A["①brief 후<br/>글감 픽<br/>(A/B/C 중 1)"] -->
    B["②angle 후<br/>thesis 픽<br/>(1/2/3 중 1)"] -->
    C["④draft 후<br/>본문 검수<br/>(OK / 수정)"] -->
    D["⑤polish 후<br/>후킹 픽<br/>(강/중/약 중 1)"] -->
    E["발행"]

    classDef pick fill:#f5a623,stroke:#a8741a,color:#000
    class A,B,C,D pick
```

각 결정에 30초~2분, **총 5~10분/편.**

---

## 4. 핵심 포인트 3가지

### ① CEO 개입은 4번뿐
- ①brief 픽 / ②angle 픽 / ④draft 검수 / ⑤polish 픽
- ③evidence는 완전 자동, CEO 개입 없음

### ② 단계 사이의 데이터 흐름
- 각 단계 output이 다음 단계 input
- ②의 픽한 thesis는 ③·④·⑤ 모두에 영향 (글의 일관성 유지)
- CEO 코멘트는 다음 단계 prompt에 자동 inject

### ③ 사이드 시스템 2개
- **judge** (자동 평가): 6점 미만이면 재생성
- **운영 DB**: CEO 픽 데이터 누적 → 100편+ 후 자동 학습 input
