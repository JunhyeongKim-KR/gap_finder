"""LLM-as-judge 평가 runner.

Usage:
    python runners/eval_runner.py --stage angle --sample sample_001.yaml
    python runners/eval_runner.py --stage angle --all

Phase A skeleton — judge prompt는 Phase B 이후 채워짐.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = ROOT / "pipeline"

STAGE_FOLDERS = {
    "brief": "stage1_brief",
    "angle": "stage2_angle",
    "evidence": "stage3_evidence",
    "draft": "stage4_draft",
    "polish": "stage5_polish",
}


def load_eval_set(stage: str, sample: str | None = None) -> list[dict]:
    eval_dir = PIPELINE_DIR / STAGE_FOLDERS[stage] / "eval"
    if not eval_dir.exists():
        return []
    files = [eval_dir / sample] if sample else sorted(eval_dir.glob("*.yaml"))
    return [yaml.safe_load(f.read_text(encoding="utf-8")) for f in files if f.exists()]


def run_eval(stage: str, sample: dict) -> dict:
    """평가 1건 실행 — Phase B 이후 judge prompt + Anthropic 호출."""
    raise NotImplementedError("judge 호출은 Phase B 이후")


def main() -> None:
    parser = argparse.ArgumentParser(description="단계별 LLM-as-judge 평가")
    parser.add_argument("--stage", required=True, choices=list(STAGE_FOLDERS))
    parser.add_argument("--sample", default=None, help="특정 sample 파일명 (생략 시 전체)")
    args = parser.parse_args()

    samples = load_eval_set(args.stage, args.sample)
    print(f"[skeleton] stage={args.stage} 평가 대상 {len(samples)}건")
    if not samples:
        print(f"[skeleton] eval set 없음 (Phase B에서 작성됨)")
        return

    for s in samples:
        run_eval(args.stage, s)


if __name__ == "__main__":
    main()
