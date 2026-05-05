# GapFinder — Claude 가이드

## 현재 상태

**5단계 파이프라인 시스템을 처음부터 짓는 중** (2026-05-05 시작, Phase A 진행).

핵심 문서:
- 시스템 구조: [`ARCH.md`](./ARCH.md)
- CEO 방향성 원문: [`board/requests/20260505_블로그운영시스템_보고서.md`](./board/requests/20260505_블로그운영시스템_보고서.md)
- CTO 액션플랜: [`board/docs/20260505_CTO_액션플랜_v2.md`](./board/docs/20260505_CTO_액션플랜_v2.md)

## 운영 모드

Claude Code 터미널 단독 운영. 슬래시 커맨드 + 자연어 혼용. Streamlit 등 별도 UI는 30편+ 누적 후 재검토.

## 슬래시 커맨드 ↔ 자연어 트리거

CEO/CTO가 자연어로 요청하면 **Claude는 반드시 매칭되는 슬래시 커맨드를 invoke**한다. 자연어 해석을 우회해 직접 답하지 말 것 — 슬래시 커맨드는 prompt 버전 관리·trace·평가의 진입점.

| 슬래시 | 단계 | 자연어 트리거 |
|--------|-----|--------------|
| `/longlist` | 사전 | "이번주 longlist", "주간 발굴", "후보 뽑아", "월요일 발굴" |
| `/brief <ticker?>` | 1 | "글감 뽑아", "글감 후보", "주제 후보" |
| `/angle <ticker>` | 2 ⭐ | "thesis 뽑아", "분석 관점", "각도 잡아", "<티커> thesis" |
| `/evidence <ticker>` | 3 | "근거 수집", "데이터 모아", "공시·재무 가져와" |
| `/draft <ticker>` | 4 | "초안 써", "본문 작성", "글 써" |
| `/polish <ticker>` | 5 | "다듬어", "팩트체크", "제목 뽑아", "후킹" |
| `/pipeline <ticker>` | 1~5 | "처음부터 끝까지", "글 1편 만들어", "<티커> 글 써줘" |
| `/publish <ticker>` | 발행 | "발행해", "올려줘", "티스토리에" |
| `/eval <stage>` | 평가 | "평가 돌려", "judge 시켜", "stage<N> 검증" |

### 슬래시 커맨드 우회 가능 (예외)
- 단순 질문/탐색 ("v0.1에 뭐 있어?", "지난주 글 보여줘")
- board/ 문서 작성 (요청·결정·리뷰)
- 시스템 설계 논의

→ 콘텐츠 생성·발행 흐름은 무조건 슬래시 커맨드 경유.

### 픽 후 자동 진행
CEO 픽이 들어오면 다음 단계 슬래시 커맨드 자동 invoke. "다음 단계 갈까요?" 묻지 않음. 단, **draft → polish는 명시적 OK 필요** (검수 단계).

## board/ 사용법

CEO·CTO·Claude 협업 기록을 보관. Claude가 자동 생성·갱신.

| 폴더 | 용도 | 트리거 |
|------|------|--------|
| `board/requests/YYYYMMDD_제목.md` | CEO 요청사항 | "요청사항 남겨줘", "이거 해달라고 전해줘" |
| `board/decisions/YYYYMMDD_제목.md` | 확정된 결정사항 | "결정했어", "이렇게 하자", "확정" |
| `board/reviews/YYYYMMDD_종목명_리뷰.md` | 결과물 피드백 | output/ 글 또는 시스템 결과에 대한 코멘트 |
| `board/docs/` | 확정 전략·계획 문서 | requests/가 docs/로 승격되는 흐름 |

요청사항 frontmatter 형식:
```markdown
---
요청자: CEO
날짜: YYYY-MM-DD
상태: 대기
---
```

## v0.1/

이전 구현(3-agent: crawler/reinterpret/writer 구조)을 통째로 격리한 폴더. **참조용으로만 보관**, 새 시스템은 v0.1/에 의존하지 않고 처음부터 재구축.

## 결정 권한 분리

- **CEO 결정**: 어떤 글, 어떤 thesis, 어떤 톤
- **CTO·시스템 결정**: 어떤 도구, 어떤 코드, 후보 몇 개, 어떤 데이터 source
- 시스템 결정 사항은 CEO에게 묻지 않음
