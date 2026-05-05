# output — 종목 분석글

이 폴더에는 GapFinder 파이프라인 3단계(글쓰기 Agent)가 생성한 **분석글**이 저장됩니다.

## 파일 규칙

```
TICKER_종목명_YYYYMMDD.md          ← 기본
TICKER_종목명_YYYYMMDD_칼럼.md     ← 칼럼 스타일
TICKER_종목명_YYYYMMDD_리포트.md   ← 리포트 스타일 (비교용)
```

## 현재 글

| 파일 | 종목/주제 | 데이터 소스 | 논점 프레임 | 작성일 |
|---|---|---|---|---|
| ① [db · 피드백전](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A0_db_%ED%94%BC%EB%93%9C%EB%B0%B1%EC%A0%84_20260406.md) | 나스닥/관세 | enriched.db only | CEO 피드백 전 | 2026-04-06 |
| ② [db+web · 피드백전](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A1_db%2Bweb_%ED%94%BC%EB%93%9C%EB%B0%B1%EC%A0%84_20260409.md) | 나스닥/관세 | enriched.db + 웹서치 | CEO 피드백 전 | 2026-04-09 |
| ③ [db · 피드백후](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A2_db_%ED%94%BC%EB%93%9C%EB%B0%B1%ED%9B%84_20260409.md) | 나스닥/관세 | enriched.db only | CEO 피드백 후 | 2026-04-09 |
| ④ [db+web · 피드백후](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A3_db%2Bweb_%ED%94%BC%EB%93%9C%EB%B0%B1%ED%9B%84_20260409.md) | 나스닥/관세 | enriched.db + 웹서치 | CEO 피드백 후 | 2026-04-09 |

## 나스닥 관세 칼럼 2×2 실험

> 상세 분석: [EXPERIMENT_나스닥관세_2x2.md](EXPERIMENT_%EB%82%98%EC%8A%A4%EB%8B%A5%EA%B4%80%EC%84%B8_2x2.md)

| | **CEO 피드백 전** | **CEO 피드백 후** |
|---|---|---|
| **enriched.db only** | [① db · 피드백전](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A0_db_%ED%94%BC%EB%93%9C%EB%B0%B1%EC%A0%84_20260406.md) | [③ db · 피드백후](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A2_db_%ED%94%BC%EB%93%9C%EB%B0%B1%ED%9B%84_20260409.md) |
| **enriched.db + 웹서치** | [② db+web · 피드백전](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A1_db%2Bweb_%ED%94%BC%EB%93%9C%EB%B0%B1%EC%A0%84_20260409.md) | [④ db+web · 피드백후](NASDAQ_%EA%B4%80%EC%84%B8_%E2%91%A3_db%2Bweb_%ED%94%BC%EB%93%9C%EB%B0%B1%ED%9B%84_20260409.md) |

**핵심 결론:** 논점이 먼저, 데이터는 그 다음이다. ③(DB only + 올바른 논점) > ②(웹서치 + 잘못된 논점).

## 글쓰기 원칙

- **칼럼니스트형 주장문** — 리포트가 아니라 주장문으로 쓴다
- 핵심 2~4개 포인트만, 나머지는 과감히 삭제
- 결론은 문장으로 명확하게
- 상세: [docs/13_writing_principles.md](../docs/13_writing_principles.md)

## 글 생성 → 검수 흐름

```
enriched.db → 글쓰기 Agent → output/ 초안 → CEO 검수 → 발행
```

1. 글쓰기 Agent가 초안 생성 → 이 폴더에 저장
2. CEO가 검수 → `board/reviews/`에 피드백
3. 수정 반영 후 확정
4. 배포 (티스토리/네이버)
