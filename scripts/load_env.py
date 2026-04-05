"""
.env 파일에서 API 키를 로드하는 유틸리티.
모든 크롤러 스크립트에서 import하여 사용.

사용법:
    from load_env import get_key
    api_key = get_key('FRED_API_KEY')
"""

import os
from pathlib import Path


ENV_PATH = Path(__file__).parent.parent / '.env'


def load_env():
    """프로젝트 루트의 .env 파일을 읽어 환경변수에 등록"""
    if not ENV_PATH.exists():
        return
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            key, value = key.strip(), value.strip()
            if value and key not in os.environ:
                os.environ[key] = value


def get_key(name):
    """API 키를 환경변수에서 가져옴. 없으면 .env에서 로드 후 재시도."""
    val = os.environ.get(name)
    if not val:
        load_env()
        val = os.environ.get(name)
    if not val:
        print(f"[경고] {name}가 설정되지 않았습니다.")
        print(f"  → .env 파일에 {name}=YOUR_KEY 형태로 추가하거나")
        print(f"  → python scripts/setup_keys.py 를 실행하세요.")
        return None
    return val


# import 시 자동 로드
load_env()
