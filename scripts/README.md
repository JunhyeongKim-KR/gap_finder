# scripts — 자동화 코드

이 폴더에는 데이터 수집과 DB 관리를 위한 **자동화 스크립트**가 들어있습니다.
CTO가 관리하는 영역이며, CEO가 직접 실행할 필요 없습니다.

## 파일

| 파일 | 설명 |
|---|---|
| init_db.py | DB 초기화 + 샘플 데이터 입력 스크립트 |

## 예정된 스크립트

| 파일 (예정) | 설명 |
|---|---|
| collect_kr.py | 한국주식 데이터 수집 (DART, KRX, 네이버) |
| collect_us.py | 미국주식 데이터 수집 (Yahoo Finance, SEC) |
| collect_macro.py | 매크로 데이터 수집 (FRED, 한은) |
| update_db.py | 수집 데이터 → DB 업데이트 |
