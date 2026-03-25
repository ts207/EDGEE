import subprocess
from pathlib import Path
import ast
import re

def main():
    root = Path("/home/irene/Edge/Edge")
    pipe_dir = root / "project" / "pipelines" / "research"
    research_dir = root / "project" / "research"
    
    keep = {"__init__.py", "phase2_candidate_discovery.py", "promote_candidates.py"}
    
    moved_modules = set()
    
    for f in pipe_dir.glob("*.py"):
        if f.name in keep:
            continue
        
        dest = research_dir / f.name
        if dest.exists():
            print(f"WARNING: {dest} already exists! Skipping move for {f.name}.")
            # But we still want to rewrite its imports if it was previously moved
            moved_modules.add(f.stem)
            continue
            
        print(f"Moving {f.name} to project/research/")
        subprocess.run(["git", "mv", str(f), str(dest)], check=True)
        moved_modules.add(f.stem)
        
    print(f"Moved {len(moved_modules)} modules.")
    
    def rewrite_file(filepath):
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return
            
        if "project.pipelines.research" not in content and "pipelines.research" not in content:
            return
            
        # We will use Regex with negative lookaheads to be safe, because AST manipulation 
        # strips comments and formatting.
        # We want to replace "project.pipelines.research" with "project.research"
        # UNLESS the very next identifier is "phase2_candidate_discovery" or "promote_candidates" or "cli".
        
        # Regex explanation:
        # Match project.pipelines.research
        # Not followed by .phase2_candidate_discovery or .promote_candidates or .cli
        # Not followed by import phase2... (with optional parens/newlines)
        
        # Actually, simpler: just blanket replace, then revert the specific ones!
        new_content = content.replace("project.pipelines.research", "project.research")
        
        # Revert the kept modules:
        for kept in ["phase2_candidate_discovery", "promote_candidates", "cli"]:
            # Revert direct attribute access
            new_content = new_content.replace(
                f"project.research.{kept}",
                f"project.pipelines.research.{kept}"
            )
            # Revert from imports (e.g. from project.research import phase2_candidate_discovery)
            # This is tricky because of `from project.research import ( ... phase2_candidate_discovery ... )`
            # For this codebase, let's just use regex to fix `import ... kept` where the context is project.research
            # Actually, `import project.research.phase2_candidate_discovery` is fixed above.
            # What about `from project.research import phase2_candidate_discovery`?
            new_content = re.sub(
                r"from\s+project\.research\s+import\s+(.*?)\b" + kept + r"\b",
                lambda m: f"from project.pipelines.research import {m.group(1)}{kept}" if "from project.research" in m.group(0) else m.group(0),
                new_content,
                flags=re.DOTALL
            )
            
        if new_content != content:
            filepath.write_text(new_content, encoding="utf-8")
            print(f"Updated imports in {filepath.relative_to(root)}")

    all_py_files = []
    all_py_files.extend((root / "project").rglob("*.py"))
    all_py_files.extend((root / "tests").rglob("*.py"))
    for pf in all_py_files:
        rewrite_file(pf)

if __name__ == "__main__":
    main()
