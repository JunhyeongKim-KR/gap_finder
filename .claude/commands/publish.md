---
description: 5단계 픽 후 티스토리 자동 발행
allowed-tools: Bash, Read, Write
argument-hint: "<ticker>"
---

# /publish

5단계 polish에서 후킹 픽 받은 최종 글을 티스토리에 자동 발행.

## 호출 방법
- 직접: `/publish ORCL`
- 자연어 트리거: "발행해", "올려줘", "티스토리에"

## 입력
- `data/articles/<ticker>_<YYYYMMDD>_final.md`

## 작업
1. 티스토리 OAuth 토큰 사용
2. 본문 + 제목 + 태그 → 티스토리 게시 API
3. 발행 URL → `data/articles/<ticker>_<YYYYMMDD>_published.json`
4. 운영 DB(`data/operations.db`)에 발행 기록

## 현재 상태
Phase A skeleton — 티스토리 OAuth 및 발행 API는 Phase E. 그 전엔 워드프레스 fallback 검토.
