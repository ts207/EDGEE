from __future__ import annotations

import argparse

from project.live.shadow_live_validation import DEFAULT_RUN_ID, run_shadow_live_thesis_validation


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a monitor-only shadow live validation pass over the packaged thesis store.")
    parser.add_argument("--thesis-store", required=True)
    parser.add_argument("--data-root")
    parser.add_argument("--out-dir")
    parser.add_argument("--docs-dir")
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--window-days", type=int, default=14)
    parser.add_argument("--context-window-bars", type=int, default=3)
    args = parser.parse_args()
    run_shadow_live_thesis_validation(
        thesis_store_path=args.thesis_store,
        data_root=args.data_root,
        out_dir=args.out_dir,
        docs_dir=args.docs_dir,
        run_id=args.run_id,
        window_days=args.window_days,
        context_window_bars=args.context_window_bars,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
