from __future__ import annotations
from project.research.cli.promotion_cli import run_promotion_cli
if __name__ == "__main__":
    import sys
    sys.exit(run_promotion_cli(sys.argv[1:]).exit_code)
