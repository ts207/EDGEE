import ast
import os
import re

base_dir = r"c:\Users\tuvsh\Downloads\Edge\Edge"
events_dir = os.path.join(base_dir, "project", "events")

# 1. Parse YAML to get parameters for each event
yaml_path = os.path.join(base_dir, "spec", "events", "event_registry_unified.yaml")
with open(yaml_path, "r", encoding="utf-8") as f:
    text = f.read()

events_block = text.split("events:")[1] if "events:" in text else ""
yaml_params = {}

blocks = re.split(r"^  ([A-Z0-9_]+):", events_block, flags=re.MULTILINE)
for i in range(1, len(blocks), 2):
    event_name = blocks[i]
    body = blocks[i+1]
    
    params = {}
    if "    parameters:" in body:
        # crude but effective block extraction
        param_block = body.split("    parameters:")[1].split("    templates:")[0].split("    horizons:")[0]
        # remove calibration and similar nested dicts by simple logic: skip if indent > 6
        for line in param_block.split("\n"):
            if line.startswith("      ") and not line.startswith("       ") and ":" in line:
                k = line.split(":")[0].strip()
                v = line.split(":")[1].strip()
                if k != "" and v != "" and k not in ('notes', 'canonical_family', 'detector_contract', 'calibration', 'expected_behavior', 'detector'):
                    params[k] = v
    yaml_params[event_name] = params

# 2. Map detectors
detectors_yml = os.path.join(base_dir, "project", "configs", "registries", "detectors.yaml")
mapping = {}
with open(detectors_yml, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("  ") and ":" in line:
            parts = line.split(":")
            if len(parts) == 2:
                mapping[parts[0].strip()] = parts[1].strip()

class_to_events = {}
for ev, cls in mapping.items():
    if cls not in class_to_events:
        class_to_events[cls] = []
    class_to_events[cls].append(ev)

# 3. Analyze Python code using AST
class DetectorVisitor(ast.NodeVisitor):
    def __init__(self):
        self.current_class = None
        self.classes = {}
        
    def visit_ClassDef(self, node):
        old_class = self.current_class
        self.current_class = node.name
        self.classes[node.name] = {'params_get': set(), 'hardcoded_nums': set()}
        self.generic_visit(node)
        self.current_class = old_class
        
    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == "get":
            # params.get or self.defaults.get
            if len(node.args) > 0 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                if self.current_class:
                    self.classes[self.current_class]['params_get'].add(node.args[0].value)
        self.generic_visit(node)
        
    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)) and self.current_class:
            if node.value not in (0, 1, 0.0, 1.0, -1, 2, 2.0, 3, 100, 100.0, 10000.0, 1e-12):
                if not (isinstance(node.value, int) and node.value < 10):
                    self.classes[self.current_class]['hardcoded_nums'].add(node.value)
        self.generic_visit(node)

visitor = DetectorVisitor()
for root, _, files in os.walk(events_dir):
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, "r", encoding="utf-8") as fp:
                try:
                    tree = ast.parse(fp.read(), filename=path)
                    visitor.visit(tree)
                except Exception as e:
                    pass

# 4. Compare
audit_report = []
issue_count = 0

for cls, info in visitor.classes.items():
    if cls not in class_to_events:
        continue
    events = class_to_events[cls]
    for ev in events:
        y_params = yaml_params.get(ev, {})
        py_params = info['params_get']
        
        unused_yaml = [p for p in y_params.keys() if p not in py_params]
        missing_in_yaml = [p for p in py_params if p not in y_params.keys() and not p.startswith("context_")]
        hardcoded = info['hardcoded_nums']
        
        if unused_yaml or missing_in_yaml or hardcoded:
            has_issues = False
            lines = [f"### Event: {ev} (`{cls}`)"]
            if unused_yaml:
                lines.append(f"- ⚠️ **Unused YAML Spec Parameters**: {unused_yaml}")
                has_issues = True
            if missing_in_yaml:
                valid_missing = [m for m in missing_in_yaml if not m.startswith('intensity') and m not in ('name', 'id', 'type')]
                if valid_missing:
                    lines.append(f"- ❓ **Implicit Code Parameters (Not in YAML)**: {valid_missing}")
                    has_issues = True
            if hardcoded:
                suspicious = [h for h in hardcoded if 0.0 < h < 1.0 or h in (96, 288, 2880, 12, 24, 48)]
                if suspicious:
                    lines.append(f"- 🔴 **Suspicious Hardcodings in Python**: {sorted(suspicious)}")
                    has_issues = True
                    
            if has_issues:
                audit_report.extend(lines)
                audit_report.append("")
                issue_count += 1

with open(os.path.join(base_dir, "deep_coverage_audit.md"), "w", encoding="utf-8") as f:
    f.write(f"# Deep Parameter Audit Report\nTotal Events with Config Drifts: {issue_count}\n\n")
    f.write("\n".join(audit_report))

print("done")
