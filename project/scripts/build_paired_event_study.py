from __future__ import annotations

import argparse

from project.research.paired_event_study import DEFAULT_CANDIDATE_ID, build_direct_paired_event_study


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the direct paired-event study artifact for a packaged bridge thesis.")
    parser.add_argument("--candidate-id", default=DEFAULT_CANDIDATE_ID)
    parser.add_argument("--policy")
    parser.add_argument("--data-root")
    parser.add_argument("--docs-dir")
    args = parser.parse_args()
    build_direct_paired_event_study(
        candidate_id=args.candidate_id,
        policy_path=args.policy,
        data_root=args.data_root,
        docs_dir=args.docs_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
