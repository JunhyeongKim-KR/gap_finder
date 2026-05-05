"""5단계 파이프라인 chain runner.

Usage:
    python runners/pipeline.py --stage all --ticker ORCL
    python runners/pipeline.py --stage angle --ticker ORCL

Phase A skeleton — 실제 LLM 호출은 Phase B 이후.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
PIPELINE_DIR = ROOT / "pipeline"
DATA_DIR = ROOT / "data"

STAGES: list[str] = ["brief", "angle", "evidence", "draft", "polish"]
STAGE_FOLDERS: dict[str, str] = {
    "brief": "stage1_brief",
    "angle": "stage2_angle",
    "evidence": "stage3_evidence",
    "draft": "stage4_draft",
    "polish": "stage5_polish",
}
STAGE_MODELS: dict[str, str] = {
    "brief": "claude-sonnet-4-6",
    "angle": "claude-opus-4-7",
    "evidence": "claude-sonnet-4-6",
    "draft": "claude-sonnet-4-6",
    "polish": "claude-sonnet-4-6",
}


def load_prompt(stage: str) -> str:
    """단계별 prompt.md 로드."""
    folder = STAGE_FOLDERS[stage]
    return (PIPELINE_DIR / folder / "prompt.md").read_text(encoding="utf-8")


def run_stage(stage: str, ticker: str, context: dict) -> dict:
    """단일 단계 실행. Phase B 이후 실제 Anthropic SDK 호출 추가."""
    prompt = load_prompt(stage)
    model = STAGE_MODELS[stage]
    print(f"[skeleton] stage={stage} model={model} ticker={ticker}")
    print(f"[skeleton] prompt 길이={len(prompt)} chars")
    raise NotImplementedError(f"stage {stage} 실행은 Phase B 이후 구현")


def save_output(stage: str, ticker: str, payload: dict) -> Path:
    """단계 산출물 저장."""
    out_dir = DATA_DIR / "candidates"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{ticker}_{stage}.json"
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="GapFinder 5-stage pipeline")
    parser.add_argument("--stage", default="all", choices=["all", *STAGES])
    parser.add_argument("--ticker", required=True)
    args = parser.parse_args()

    if args.stage == "all":
        ctx: dict = {}
        for s in STAGES:
            ctx[s] = run_stage(s, args.ticker, ctx)
    else:
        run_stage(args.stage, args.ticker, {})


if __name__ == "__main__":
    main()
