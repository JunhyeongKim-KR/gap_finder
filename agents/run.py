"""
GapFinder 파이프라인 실행기

사용법:
    python agents/run.py crawl                # 전체 크롤링
    python agents/run.py crawl --source stocks  # 종목만
    python agents/run.py reinterpret            # (미구현)
    python agents/run.py write                  # (미구현)
    python agents/run.py publish                # (미구현)
"""

import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

SCRIPTS_DIR = Path(__file__).parent / 'crawler'

CRAWLERS = {
    'stocks': 'collect_stocks.py',
    'macro':  'collect_macro.py',
    'events': 'collect_events.py',
    'energy': 'collect_energy.py',
    'trade':  'collect_trade.py',
}


def run_script(name, extra_args=None):
    """스크립트 실행 후 결과 반환"""
    path = SCRIPTS_DIR / name
    cmd = [sys.executable, str(path)]
    if extra_args:
        cmd.extend(extra_args)
    print(f"\n{'='*50}")
    print(f"  실행: {name}")
    print(f"{'='*50}")
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
    return result.returncode


def cmd_crawl(args):
    """1단계: raw DB 크롤링"""
    print(f"\n[1단계] raw DB 크롤링 시작 — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    extra = []
    if args.days:
        extra.extend(['--days', str(args.days)])

    if args.source == 'all':
        targets = CRAWLERS.items()
    else:
        name = CRAWLERS.get(args.source)
        if not name:
            print(f"[에러] 알 수 없는 소스: {args.source}")
            print(f"  가능한 값: {', '.join(CRAWLERS.keys())}")
            return
        targets = [(args.source, name)]

    results = {}
    for source, script in targets:
        rc = run_script(script, extra)
        results[source] = 'OK' if rc == 0 else f'에러 (code {rc})'

    print(f"\n{'='*50}")
    print(f"  크롤링 완료 — {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*50}")
    for source, status in results.items():
        print(f"  {source:10s} : {status}")
    print()


def cmd_reinterpret(args):
    """2단계: 재해석 (미구현)"""
    print("[2단계] 재해석 — 미구현")
    print("  → docs/14_agent_reinterpret.md 참조")


def cmd_write(args):
    """3단계: 글쓰기 (미구현)"""
    print("[3단계] 글쓰기 — 미구현")
    print("  → docs/15_agent_writer.md 참조")


def cmd_publish(args):
    """4단계: 배포 (미구현)"""
    print("[4단계] 배포 — 미구현")


def main():
    parser = argparse.ArgumentParser(
        description='GapFinder 4단계 파이프라인',
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest='command')

    # 1. crawl
    p_crawl = sub.add_parser('crawl', help='1단계: raw DB 크롤링')
    p_crawl.add_argument('--source', default='all',
                         help='stocks / macro / events / energy / trade / all')
    p_crawl.add_argument('--days', type=int, default=None,
                         help='수집 기간 (일)')
    p_crawl.set_defaults(func=cmd_crawl)

    # 2. reinterpret
    p_re = sub.add_parser('reinterpret', help='2단계: 재해석 (미구현)')
    p_re.set_defaults(func=cmd_reinterpret)

    # 3. write
    p_wr = sub.add_parser('write', help='3단계: 글쓰기 (미구현)')
    p_wr.set_defaults(func=cmd_write)

    # 4. publish
    p_pub = sub.add_parser('publish', help='4단계: 배포 (미구현)')
    p_pub.set_defaults(func=cmd_publish)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == '__main__':
    main()
