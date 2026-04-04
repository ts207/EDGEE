import argparse
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preset", type=str, required=True, help="Preset name (e.g. core_v1)")
    args = parser.parse_args()

    print(f"Starting certification cycle for {args.preset}...")
    
    # 1. Run Benchmark Matrix
    print("Running benchmark matrix...")
    ret = subprocess.call([sys.executable, "-m", "project.scripts.run_benchmark_matrix", "--preset", args.preset])
    if ret != 0:
        print("Benchmark matrix failed.")
        return ret
        
    # 2. Show Review Artifact
    print("Generating review artifact...")
    subprocess.call([sys.executable, "-m", "project.scripts.show_benchmark_review", "--latest"])
    
    print("Certification cycle completed.")
    return 0
    
if __name__ == "__main__":
    main()
