# board — CEO·CTO 소통 + 전략 문서

## 구조

```
board/
├── requests/    ← 인큐베이터 (CEO 요청, 초안, 피드백)
└── docs/        ← 확정 전략 (검토 완료, 졸업 전)
```

## 흐름

```
requests/  →  docs/  →  agents/, db/
(요청)       (확정)     (최종 위치)
```

- CEO가 요청/피드백 → requests/에 저장
- CTO가 검토·확정 → docs/로 이동
- 특정 컴포넌트에 속하면 → agents/, db/ 등으로 졸업
