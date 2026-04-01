from __future__ import annotations

from project.research.seed_empirical import run_empirical_seed_pass


if __name__ == "__main__":
    out = run_empirical_seed_pass()
    print(f"wrote: {out['csv']}")
    print(f"wrote: {out['json']}")
    print(f"wrote: {out['md']}")
