from __future__ import annotations
from project.research.cli.candidate_discovery_cli import run_candidate_discovery_cli as main
if __name__ == "__main__":
    import sys
    sys.exit(main(sys.argv[1:]))
