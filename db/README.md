# db — 종목 데이터베이스

이 폴더에는 종목 정보가 저장된 **SQLite 데이터베이스**가 들어있습니다.
CEO가 직접 열 필요 없이, Claude에게 물어보면 데이터를 조회해줍니다.

## 파일

| 파일 | 설명 |
|---|---|
| gapfinder.db | 종목 마스터, 재무 데이터, 시세, 매크로 이벤트, 발행 이력 |

## 조회 방법

Claude에게 자연어로 물어보면 됩니다:
```
"삼성전자 현재 DB에 저장된 정보 보여줘"
"지금 DB에 몇 개 종목 있어?"
"삼성전자 최근 재무 데이터 알려줘"
```

## DB 구조 (참고)

자세한 설계는 [docs/04_database_design.md](../docs/04_database_design.md) 참고.

| 테이블 | 내용 |
|---|---|
| stock_master | 종목 기본 정보, 투자 논거, 판단 |
| financials | 분기별 재무 데이터 |
| price_daily | 일별 시세 |
| macro_events | 매크로 이벤트 |
| content_log | 콘텐츠 발행 이력 |
