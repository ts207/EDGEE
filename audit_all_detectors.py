import os, re

base_dir = r"c:\Users\tuvsh\Downloads\Edge\Edge"
events_path = os.path.join(base_dir, "spec", "events", "event_registry_unified.yaml")
detectors_path = os.path.join(base_dir, "project", "configs", "registries", "detectors.yaml")

with open(events_path, "r", encoding="utf-8") as f:
    text = f.read()

events_block = text.split("events:")[1] if "events:" in text else ""
active_events = []
alias_events = []

blocks = re.split(r"^  ([A-Z0-9_]+):", events_block, flags=re.MULTILINE)
for i in range(1, len(blocks), 2):
    event_name = blocks[i]
    event_body = blocks[i+1]
    
    # Simple checks
    if "alias_for:" in event_body:
        alias_events.append(event_name)
    elif "active: false" in event_body:
        pass
    else:
        active_events.append(event_name)

detector_map = {}
with open(detectors_path, "r", encoding="utf-8") as f:
    for line in f:
        if line.startswith("  ") and ":" in line:
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip()
                val = parts[1].strip()
                if key and val:
                    detector_map[key] = val

missing = [e for e in active_events if e not in detector_map]
orphan = [e for e in detector_map if e not in active_events and e not in alias_events]

print(f"Total Active Events: {len(active_events)}")
print(f"Total Aliases: {len(alias_events)}")
print(f"Total Mapped Detectors in detectors.yaml: {len(detector_map)}")
print(f"Missing: {len(missing)}")
print(f"Orphans: {len(orphan)}")

with open(os.path.join(base_dir, "audit_results.md"), "w", encoding="utf-8") as out:
    out.write("### Events Without Detectors (Missing Coverage)\n")
    for e in sorted(missing):
        out.write(f"- {e}\n")
    
    out.write("\n### Detectors Mapped to Unknown Events (Orphans)\n")
    for e in sorted(orphan):
        out.write(f"- {e} -> {detector_map[e]}\n")
        
    out.write("\n### Full Detector Mapping\n")
    out.write("| Event | Detector Class |\n")
    out.write("|-------|----------------|\n")
    for e in sorted(active_events):
        if e in detector_map:
            out.write(f"| {e} | {detector_map[e]} |\n")
        else:
            out.write(f"| {e} | **MISSING** |\n")

print("done")
