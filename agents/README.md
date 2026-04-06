# agents — 4단계 파이프라인

각 Agent/스크립트는 **자기 폴더 안의 문서만** 참조한다.

## 구조

```
agents/
├── crawler/            ← 1단계: 크롤링 (토큰 X)
│   ├── collect_*.py    ← 크롤링 스크립트 5종
│   ├── init_*.py       ← DB 초기화
│   ├── load_env.py     ← API 키 로드
│   └── architecture.md ← 크롤링 구조 설계

├── reinterpret/        ← 2단계: 재해석 Agent (토큰 O)
│   ├── PROMPT.md       ← Agent 지시문
│   └── philosophy.md   ← 투자 철학 22개 프레임

└── writer/             ← 3단계: 글쓰기 Agent (토큰 O)
    ├── PROMPT.md       ← Agent 지시문
    ├── writing.md      ← 글쓰기 12원칙 + 4패턴
    └── template.md     ← 글 템플릿 (참조용)
```

## 실행

```bash
python run.py crawl              # 1단계
python run.py reinterpret        # 2단계 (미구현)
python run.py write              # 3단계 (미구현)
python run.py publish            # 4단계 (미구현)
```
