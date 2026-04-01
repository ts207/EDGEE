from __future__ import annotations

import argparse
from pathlib import Path

from project.research.thesis_evidence_runner import build_founding_thesis_evidence


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build founding-thesis evidence bundles from raw market data.")
    parser.add_argument("--policy", type=Path, default=None, help="Optional founding thesis evaluation policy path.")
    parser.add_argument("--data-root", type=Path, default=None, help="Optional data root override.")
    parser.add_argument("--docs-dir", type=Path, default=None, help="Optional docs/generated output directory override.")
    args = parser.parse_args(argv)
    build_founding_thesis_evidence(policy_path=args.policy, data_root=args.data_root, docs_dir=args.docs_dir)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
