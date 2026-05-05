# GapFinder — Claude 가이드

## 현재 상태

**5단계 파이프라인 시스템을 처음부터 짓는 중** (2026-05-05 시작).

시스템 구조: [`ARCH.md`](./ARCH.md) 참조.

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
