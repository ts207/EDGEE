from __future__ import annotations

import argparse
from pathlib import Path

from project.research.derived_confirmation import synthesize_confirmation_bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Build derived structural confirmation thesis bundles from existing component evidence.')
    parser.add_argument('--candidate-id', default='THESIS_VOL_SHOCK_LIQUIDITY_CONFIRM')
    parser.add_argument('--left', default='THESIS_VOL_SHOCK')
    parser.add_argument('--right', default='THESIS_LIQUIDITY_VACUUM')
    parser.add_argument('--data-root', type=Path, default=None)
    parser.add_argument('--docs-dir', type=Path, default=None)
    parser.add_argument('--overlap-factor', type=float, default=0.5)
    args = parser.parse_args(argv)
    synthesize_confirmation_bundle(
        candidate_id=args.candidate_id,
        component_ids=(args.left, args.right),
        data_root=args.data_root,
        docs_dir=args.docs_dir,
        overlap_factor=args.overlap_factor,
    )
    return 0


if __name__ == '__main__':  # pragma: no cover
    raise SystemExit(main())
