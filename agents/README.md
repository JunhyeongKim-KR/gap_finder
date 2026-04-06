# agents — AI Agent 전용 프롬프트

각 Agent는 **자기 폴더 안의 문서만** 참조한다. docs/를 직접 보지 않는다.

## 구조

```
agents/
├── reinterpret/          ← 2단계: 재해석 Agent
│   ├── PROMPT.md         ← Agent 지시문 (역할, 규칙, 입출력)
│   └── philosophy.md     ← 투자 철학 22개 프레임
│
└── writer/               ← 3단계: 글쓰기 Agent
    ├── PROMPT.md          ← Agent 지시문 (역할, 규칙, 입출력)
    └── writing.md         ← 글쓰기 원칙 12개 + 4패턴
```

## 원칙

- Agent가 보는 문서는 이 폴더에만 있다
- docs/ 원본이 바뀌면 여기에도 복사해서 최신화한다
- 과거 버전, 히스토리, 비교 문서는 넣지 않는다
- **최적화된 최신 전략만** 존재한다
