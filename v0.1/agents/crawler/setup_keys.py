"""
API 키 설정 스크립트.
대화형으로 키를 입력받아 .env 파일에 저장.

사용법:
    python scripts/setup_keys.py
"""

from pathlib import Path

ENV_PATH = Path(__file__).parent.parent.parent / '.env'

KEYS = [
    ('FRED_API_KEY', 'FRED (미국 거시)', 'https://fred.stlouisfed.org/docs/api/api_key.html'),
    ('ECOS_API_KEY', 'ECOS (한국은행)', 'https://ecos.bok.or.kr/api/#/AuthKeyApply'),
    ('DART_API_KEY', 'OpenDART (한국 공시)', 'https://opendart.fss.or.kr'),
    ('EIA_API_KEY', 'EIA (미국 에너지)', 'https://www.eia.gov/opendata/register.php'),
    ('BLS_API_KEY', 'BLS (미국 고용)', 'https://data.bls.gov/registrationEngine/'),
    ('KRX_API_KEY', 'KRX (한국거래소)', 'https://data.krx.co.kr'),
    ('DATA_GO_KR_API_KEY', '관세청/공공데이터포털', 'https://data.go.kr'),
]


def load_existing():
    """기존 .env 파일의 키-값 로드"""
    existing = {}
    if ENV_PATH.exists():
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                existing[key.strip()] = value.strip()
    return existing


def main():
    print("=" * 50)
    print("  GapFinder API 키 설정")
    print("=" * 50)
    print()
    print("각 소스의 API 키를 입력하세요.")
    print("이미 설정된 키는 [****] 로 표시됩니다.")
    print("변경하지 않으려면 Enter를 누르세요.")
    print()

    existing = load_existing()
    updated = dict(existing)

    for key_name, description, url in KEYS:
        current = existing.get(key_name, '')
        if current:
            display = current[:4] + '****' + current[-4:]
            prompt = f"  {description}\n  현재: [{display}]\n  새 키 (Enter=유지): "
        else:
            prompt = f"  {description}\n  등록: {url}\n  키 입력 (Enter=건너뛰기): "

        new_val = input(prompt).strip()
        if new_val:
            updated[key_name] = new_val
            print(f"  → 설정됨\n")
        elif current:
            print(f"  → 유지\n")
        else:
            print(f"  → 건너뜀\n")

    # .env 파일 저장
    with open(ENV_PATH, 'w') as f:
        for key_name, _, _ in KEYS:
            val = updated.get(key_name, '')
            f.write(f"{key_name}={val}\n")

    print("=" * 50)
    print(f"  .env 저장 완료: {ENV_PATH}")
    print()

    # 상태 요약
    set_count = sum(1 for k, _, _ in KEYS if updated.get(k))
    total = len(KEYS)
    print(f"  설정됨: {set_count}/{total}")
    for key_name, desc, _ in KEYS:
        val = updated.get(key_name, '')
        status = "✓" if val else "✗"
        print(f"    {status} {desc}")
    print()


if __name__ == '__main__':
    main()
