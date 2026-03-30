from __future__ import annotations

import argparse
import logging
from pathlib import Path

from project.research.live_export import export_promoted_theses_for_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Export live-usable promoted thesis payloads.")
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--data_root", default=None)
    args = parser.parse_args(argv)

    result = export_promoted_theses_for_run(
        args.run_id,
        data_root=Path(args.data_root) if args.data_root else None,
    )
    logging.info(
        "Exported %s theses for %s to %s",
        result.thesis_count,
        result.run_id,
        result.output_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
