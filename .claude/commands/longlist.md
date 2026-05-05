---
description: 매주 월요일 후보 15개 자동 산출 (universe 850종목 → 5개 trigger 필터 → 검색량 필터 → 상위 15)
allowed-tools: Bash, Read, Write
---

# /longlist

매주 월요일 글감 후보 15개 자동 산출.

## 호출 방법
- 직접: `/longlist`
- 자연어 트리거: "이번주 longlist", "주간 발굴", "후보 뽑아", "월요일 발굴"

## 작업
1. `runners/longlist.py` 실행 — Phase A는 skeleton 단계라 NotImplementedError 발생.
2. Phase C 이후 정상 동작.
3. 결과는 `data/candidates/longlist_<YYYY-MM-DD>.json` 에 저장.

## 출력 형식 (Phase C 이후)
```
주간 발굴 — YYYY/MM/DD ~ YYYY/MM/DD
01. 종목명 (티커) — 트리거 종류
    "1줄 요약"
... (총 15개)
```

CEO 픽 + 코멘트 → `/brief` 자동 호출.
