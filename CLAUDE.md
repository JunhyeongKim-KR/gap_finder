# GapFinder — Claude 가이드

## 이 프로젝트는
역발상 투자 리서치 콘텐츠 시스템. 종목 DB에서 데이터를 읽고, 분석 글을 생성하고, 매크로 이슈 발생 시 관련 종목을 업데이트하는 반자동 체계.

## 팀 역할
- **CEO**: 기획·판단·콘텐츠 방향. 코드를 모름. 자연어로만 소통.
- **CTO**: 개발·자동화·DB·코드. 시스템 설계와 구현.
- **Claude**: CEO/CTO 요청에 따라 글 초안 생성, DB 조회, 문서 작성, 요청서 정리.

## CEO가 요청할 때 행동 규칙

### 요청사항 남기기
- CEO가 "요청사항 남겨줘", "이거 해달라고 전해줘" 등을 말하면
- `board/requests/YYYYMMDD_제목.md` 파일을 생성
- 형식:
```markdown
---
요청자: CEO
날짜: YYYY-MM-DD
상태: 대기
---
# 요청 제목
## 내용
(요청 내용)
## 기대 결과
(어떤 결과물이 나와야 하는지)
```

### 결정사항 기록
- "결정했어", "이렇게 하자", "확정" 등의 표현 시
- `board/decisions/YYYYMMDD_제목.md` 파일을 생성

### 리뷰/피드백 기록
- output/ 글에 대한 피드백 시
- `board/reviews/YYYYMMDD_종목명_리뷰.md` 파일을 생성

### 종목 분석 글 생성
- docs/07_article_template.md 의 표준 템플릿을 따를 것
- db/gapfinder.db 에서 해당 종목 데이터를 먼저 조회
- output/TICKER_종목명_YYYYMMDD.md 로 저장
- docs/08_risk_control.md 의 작성 원칙을 반드시 준수

### 진행 상황 질문
- "진행 상황", "어디까지 왔어", "현황" 등 질문 시
- status/progress.md 를 읽어서 요약
- status/coverage.md 로 종목 현황 안내

## 파일 네이밍 규칙
- 요청: `board/requests/YYYYMMDD_제목.md`
- 결정: `board/decisions/YYYYMMDD_제목.md`
- 리뷰: `board/reviews/YYYYMMDD_종목명_리뷰.md`
- 분석글: `output/TICKER_종목명_YYYYMMDD.md`
- 진행상황 업데이트 시 status/ 파일도 함께 갱신

## 작성 원칙 (반드시 준수)
1. 확인되지 않은 수치는 절대 단정하지 말 것
2. 공식 자료 확인 시에만 숫자 제시
3. 불확실하면 "확인되지 않으나…", "가설적 추론 전제" 표현 사용
4. 사실·해석·추론을 반드시 구분
5. 목표주가는 시나리오와 가정에 따라 제시
6. 철회조건은 '가격'이 아니라 '가설 붕괴 조건'으로 정의

## 시스템 구조 (5영역)

### 파이프라인 (4단계)
1. **raw DB 크롤링** (토큰X): scripts/collect_*.py → db/raw.db
2. **DB 구축/재해석** (토큰O): agents/reinterpret/ 참조
3. **글쓰기** (토큰O): agents/writer/ 참조
4. **배포** (토큰X): 자동화 스크립트 → 티스토리/네이버

### Agent
- 재해석 Agent: agents/reinterpret/ (PROMPT.md + philosophy.md)
- 글쓰기 Agent: agents/writer/ (PROMPT.md + writing.md)
- 각 Agent는 자기 폴더 안의 문서만 참조. docs/ 직접 참조 금지.

### DB
- DB 설계: docs/04_database_design.md
- 데이터 파이프라인: docs/10_data_pipeline.md

### 운영
- 플랫폼: docs/02_platform_strategy.md
- 로드맵: docs/06_roadmap.md
- 체크리스트: docs/09_checklist.md

글의 기본 문법: [시장 컨센서스] → [해석의 맹점] → [실제 메커니즘] → [진짜 수혜/피해] → [체크포인트]

## 참고 문서 위치
- 전략 문서: docs/ (01~15)
- DB 설계: docs/04_database_design.md
- 글 템플릿: docs/07_article_template.md
- 체크리스트: docs/09_checklist.md
- 데이터 파이프라인: docs/10_data_pipeline.md
- 투자 철학: docs/12_investment_philosophy.md
- 글쓰기 원칙: docs/13_writing_principles.md
