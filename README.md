# GapFinder

**역발상 투자 리서치 콘텐츠 시스템**

종목 DB 구축 → 개별 종목 분석 → 매크로 이슈 연동 업데이트 → 플랫폼별 재가공 → 자동 업로드까지 이어지는 반자동 투자 콘텐츠 운영 체계.

## 핵심 철학

- "좋은 회사인가"가 아니라 **"현재 시장 기대가 과도한가"**를 분석 축으로
- 역발상(Contrarian) 기반 중기 매매 — 3~12개월 재평가 가능성 중심
- 시장의 비관/낙관이 과도한 구간에서 실제 사업가치와의 괴리를 찾아냄

## 문서 구조

| 문서 | 설명 |
|---|---|
| [docs/01_business_assessment.md](docs/01_business_assessment.md) | 사업성 평가 |
| [docs/02_platform_strategy.md](docs/02_platform_strategy.md) | 플랫폼 전략 |
| [docs/03_stock_selection.md](docs/03_stock_selection.md) | 종목 선정 철학 |
| [docs/04_database_design.md](docs/04_database_design.md) | DB 설계안 |
| [docs/05_macro_update_system.md](docs/05_macro_update_system.md) | 매크로 업데이트 체계 |
| [docs/06_roadmap.md](docs/06_roadmap.md) | 초기 3개월 로드맵 |
| [docs/07_article_template.md](docs/07_article_template.md) | 종목 글 표준 템플릿 |
| [docs/08_risk_control.md](docs/08_risk_control.md) | 운영 리스크 통제 |
| [docs/09_checklist.md](docs/09_checklist.md) | 실행 체크리스트 |
| [docs/10_data_pipeline.md](docs/10_data_pipeline.md) | 데이터 파이프라인 설계 |
| [docs/11_pdf_comparison.md](docs/11_pdf_comparison.md) | 기존 PDF 전략 비교 분석 |

## 시각화

- [viz/index.html](viz/index.html) — 전체 시스템 대시보드

## 프로젝트 구조 (예정)

```
gap_finder/
├── docs/           # 전략 문서
├── viz/            # 시각화 HTML
├── scripts/        # 데이터 수집·가공 스크립트
├── db/             # SQLite DB
├── raw/            # 원본 수집 데이터
├── output/         # 생성된 글 초안
└── templates/      # 프롬프트·글 템플릿
```
