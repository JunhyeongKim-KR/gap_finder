# db — 데이터베이스

GapFinder의 모든 데이터가 저장되는 SQLite DB 2개.

## DB 구조

| DB | 파일 | 역할 | 누가 쓰는가 |
|---|---|---|---|
| **raw.db** | `db/raw.db` | 크롤링한 날것 데이터 저장 | 크롤링 스크립트 (1단계) |
| **enriched.db** | `db/enriched.db` | 재해석 Agent가 맥락/비교/프레임 해석을 부여한 데이터 | 재해석 Agent (2단계) |

## 흐름
```
인터넷 → 크롤링 스크립트 → raw.db → 재해석 Agent → enriched.db → 글쓰기 Agent → output/
```

## 관리
- raw.db: 크롤링 스크립트가 자동으로 관리 (사람이 직접 편집하지 않음)
- enriched.db: 재해석 Agent가 관리 (사람이 직접 편집하지 않음)
- CEO는 viz/ 대시보드에서 데이터 확인
