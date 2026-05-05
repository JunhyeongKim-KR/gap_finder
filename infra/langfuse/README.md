# Langfuse self-host (Phase A 후반)

LLMOps 인프라 — 프롬프트 버전 관리 + AI 호출 추적 + 비용 모니터링.

## 도입 시점
Phase A 후반에 Docker Compose로 배포. Phase B 시연 시 trace 기록 필수.

## 설치 (예정)
```bash
# Phase A 후반에 작성
docker compose up -d
# → http://localhost:3000
```

## 환경 변수
- `LANGFUSE_HOST` — 기본 http://localhost:3000
- `LANGFUSE_PUBLIC_KEY`
- `LANGFUSE_SECRET_KEY`

각 키는 self-host 배포 후 admin UI 에서 발급.

## 현재 상태
SKELETON. docker-compose.yml 은 미생성.
