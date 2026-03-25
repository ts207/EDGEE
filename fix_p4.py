import os
import glob
import re

base_dir = r"c:\Users\tuvsh\Downloads\Edge\Edge"
events_dir = os.path.join(base_dir, "spec", "events")

proxies = {
    "ABSORPTION_PROXY": "LIQUIDITY_DISLOCATION",
    "DEPTH_STRESS_PROXY": "LIQUIDITY_DISLOCATION",
    "FLOW_EXHAUSTION_PROXY": "FORCED_FLOW_AND_EXHAUSTION",
    "LIQUIDATION_EXHAUSTION_REVERSAL": "FORCED_FLOW_AND_EXHAUSTION",
    "LIQUIDITY_STRESS_DIRECT": "LIQUIDITY_DISLOCATION",
    "LIQUIDITY_STRESS_PROXY": "LIQUIDITY_DISLOCATION",
    "PRICE_VOL_IMBALANCE_PROXY": "LIQUIDITY_DISLOCATION",
    "WICK_REVERSAL_PROXY": "FORCED_FLOW_AND_EXHAUSTION"
}

# 1. Update all yaml files in spec/events/ to use the right canonical_family
for filepath in glob.glob(os.path.join(events_dir, "**/*.yaml"), recursive=True):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    modified = False
    for proxy, canonical in proxies.items():
        if f"canonical_family: {proxy}" in content:
            content = content.replace(f"canonical_family: {proxy}", f"canonical_family: {canonical}")
            modified = True
    
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

# 2. Remove families from event_registry_unified.yaml
unified_path = os.path.join(events_dir, "event_registry_unified.yaml")
if os.path.exists(unified_path):
    with open(unified_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    new_lines = []
    skip = False
    for line in lines:
        if line.startswith("  ") and not line.startswith("    "):
            family_name = line.strip().rstrip(":")
            if family_name in proxies:
                skip = True
            else:
                skip = False
        
        if not skip:
            new_lines.append(line)
            
    with open(unified_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


# 3. Add intersections to search_space.yaml
search_space_path = os.path.join(base_dir, "spec", "search_space.yaml")
with open(search_space_path, "r", encoding="utf-8") as f:
    ss_content = f.read()

if "conditioning_intersections:" not in ss_content:
    intersections = """
# Cross-family state conditioning intersections
conditioning_intersections:
  - CROWDING_STATE + HIGH_VOL_REGIME
  - STRETCHED_STATE + LOW_FRICTION_STATE
"""
    ss_content += intersections
    with open(search_space_path, "w", encoding="utf-8") as f:
        f.write(ss_content)

# 4. Add dynamic cost to gates.yaml
gates_path = os.path.join(base_dir, "spec", "gates.yaml")
with open(gates_path, "r", encoding="utf-8") as f:
    gates_content = f.read()

if "dynamic_cost_adjustment:" not in gates_content:
    dynamic_cost = """
  dynamic_cost_adjustment:
    LIQUIDITY_DISLOCATION:
      multiplier: "spread_pct_at_event / median_spread_pct"
      target: "slippage_bps_per_fill"
"""
    gates_content = gates_content.replace("micro_min_feature_coverage: 0.25", "micro_min_feature_coverage: 0.25" + dynamic_cost)
    with open(gates_path, "w", encoding="utf-8") as f:
        f.write(gates_content)

print("done Priority 4")
