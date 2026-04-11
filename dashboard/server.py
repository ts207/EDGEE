#!/usr/bin/env python3
"""
Edge Research Platform — Backend
Run: python dashboard/server.py [port]
Default port: 7477
"""
from __future__ import annotations

import json
import pathlib
import sys
import subprocess
import threading
import uuid
import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT            = pathlib.Path(__file__).parent.parent
REPORTS         = ROOT / "data" / "reports"
LAKE_DIR        = ROOT / "data" / "lake"
SPEC_EVENTS     = ROOT / "spec" / "events"
SPEC_PROPOSALS  = ROOT / "spec" / "proposals"
SPEC_TEMPLATES  = ROOT / "spec" / "templates"
SPEC_DOMAIN     = ROOT / "spec" / "domain" / "domain_graph.yaml"
LIVE_THESES     = ROOT / "data" / "live" / "theses"
LIVE_PERSIST    = ROOT / "live" / "persist"
FEATURES_YAML   = ROOT / "project" / "configs" / "registries" / "features.yaml"
ARTIFACTS_DIR   = ROOT / "data" / "artifacts" / "experiments"
STATIC          = pathlib.Path(__file__).parent
JOBS_DIR        = STATIC / ".jobs"

# ─── Job runner ──────────────────────────────────────────────────────────────

JOBS: dict[str, dict] = {}  # job_id → job record


def start_job(cmd: list[str], label: str) -> dict:
    """Launch a subprocess, capture stdout+stderr to a log file, return job record."""
    job_id = uuid.uuid4().hex[:8]
    JOBS_DIR.mkdir(parents=True, exist_ok=True)
    log_path = JOBS_DIR / f"{job_id}.log"
    started_at = datetime.datetime.now().isoformat()
    job: dict = {
        "id":         job_id,
        "label":      label,
        "cmd":        " ".join(cmd),
        "status":     "running",
        "started_at": started_at,
        "finished_at": None,
        "exit_code":  None,
        "log_path":   str(log_path),
    }
    JOBS[job_id] = job

    def _run():
        with log_path.open("w") as fh:
            fh.write(f"# Edge Job: {label}\n# Command: {' '.join(cmd)}\n"
                     f"# Started: {started_at}\n# CWD: {ROOT}\n\n")
            fh.flush()
            try:
                proc = subprocess.Popen(
                    cmd, stdout=fh, stderr=subprocess.STDOUT,
                    cwd=str(ROOT), text=True,
                )
                job["pid"] = proc.pid
                exit_code = proc.wait()
                job["exit_code"]   = exit_code
                job["status"]      = "done" if exit_code == 0 else "failed"
            except Exception as exc:
                fh.write(f"\n# ERROR: {exc}\n")
                job["status"] = "failed"
            finally:
                job["finished_at"] = datetime.datetime.now().isoformat()

    threading.Thread(target=_run, daemon=True).start()
    return job


# ─── JSON/YAML helpers ────────────────────────────────────────────────────────

def _load_json(p: pathlib.Path) -> dict | list:
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}

def _load_yaml(p: pathlib.Path) -> dict:
    if not HAS_YAML:
        return {}
    try:
        return yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {}


# ─── Loaders ─────────────────────────────────────────────────────────────────

def load_signals() -> list[dict]:
    signals = []
    for edge_file in REPORTS.rglob("*_edge_summary.json"):
        parts = edge_file.parts
        if len(parts) < 3:
            continue
        try:
            category = parts[-3]
            run      = parts[-2]
            event    = edge_file.stem.replace("_edge_summary", "")

            edge  = _load_json(edge_file)
            stab  = _load_json(edge_file.parent / edge_file.name.replace("edge", "stability"))
            morph = _load_json(edge_file.parent / edge_file.name.replace("edge", "morphology"))
            integ = _load_json(edge_file.parent / edge_file.name.replace("edge", "integrity"))

            by_sym = edge.get("by_symbol", {})
            best_bps = (max((v.get("best_net_mean_bps", 0) for v in by_sym.values()), default=0)
                        if by_sym else 0)
            best_sym = (max(by_sym, key=lambda k: by_sym[k].get("best_net_mean_bps", 0))
                        if by_sym else None)

            stab_by_sym  = stab.get("by_symbol", {})
            morph_by_sym = morph.get("by_symbol", {})
            integ_by_sym = integ.get("by_symbol", {})

            avg_sign = (sum(v.get("sign_consistency", 0) for v in stab_by_sym.values())
                        / len(stab_by_sym) if stab_by_sym else 0)
            avg_post = (sum(v.get("post_event_return_bps", 0) for v in morph_by_sym.values())
                        / len(morph_by_sym) if morph_by_sym else 0)
            avg_pre  = (sum(v.get("pre_event_drift_bps", 0) for v in morph_by_sym.values())
                        / len(morph_by_sym) if morph_by_sym else 0)
            avg_move = (sum(v.get("event_bar_move_bps", 0) for v in morph_by_sym.values())
                        / len(morph_by_sym) if morph_by_sym else 0)

            all_months: dict[str, int] = {}
            for sv in integ_by_sym.values():
                for month, cnt in sv.get("events_per_month", {}).items():
                    all_months[month] = all_months.get(month, 0) + cnt

            sym_detail: dict[str, dict] = {}
            for sym, sv in by_sym.items():
                sym_detail[sym] = {
                    "n_events":         sv.get("n_events", 0),
                    "best_bps":         round(sv.get("best_net_mean_bps", 0), 2),
                    "best_horizon_bars": sv.get("best_horizon_bars"),
                    "sign_consistency": round(stab_by_sym.get(sym, {}).get("sign_consistency", 0), 3),
                    "overall_mean_bps": round(stab_by_sym.get(sym, {}).get("overall_mean_bps", 0), 2),
                    "post_return_bps":  round(morph_by_sym.get(sym, {}).get("post_event_return_bps", 0), 2),
                    "pre_drift_bps":    round(morph_by_sym.get(sym, {}).get("pre_event_drift_bps", 0), 2),
                    "event_bar_move_bps": round(morph_by_sym.get(sym, {}).get("event_bar_move_bps", 0), 2),
                    "cluster_rate":     round(integ_by_sym.get(sym, {}).get("cluster_rate", 0), 4),
                    "intensity_mean":   round(morph_by_sym.get(sym, {}).get("intensity_mean", 0), 3),
                    "intensity_p90":    round(morph_by_sym.get(sym, {}).get("intensity_p90", 0), 3),
                }

            signals.append({
                "id":                 f"{category}/{run}/{event}",
                "category":           category,
                "run":                run,
                "event":              event,
                "n_events":           edge.get("n_events", 0),
                "n_symbols":          edge.get("n_symbols", 0),
                "best_bps":           round(best_bps, 2),
                "best_sym":           best_sym,
                "sign_consistency":   round(avg_sign, 3),
                "post_return_bps":    round(avg_post, 2),
                "pre_drift_bps":      round(avg_pre, 2),
                "event_bar_move_bps": round(avg_move, 2),
                "by_symbol":          sym_detail,
                "events_per_month":   all_months,
            })
        except Exception:
            continue

    signals.sort(key=lambda x: x["best_bps"], reverse=True)
    return signals


def load_runs() -> list[dict]:
    runs = []
    phase2_dir = REPORTS / "phase2"
    if not phase2_dir.exists():
        return runs
    for diag_file in sorted(phase2_dir.glob("*/phase2_diagnostics.json")):
        try:
            run_id  = diag_file.parent.name
            diag    = _load_json(diag_file)
            burden  = _load_json(diag_file.parent / "search_burden_summary.json")
            quality = _load_json(diag_file.parent / "discovery_quality_summary.json")
            funnel  = diag.get("gate_funnel", {})
            runs.append({
                "run_id":                   run_id,
                "symbols":                  diag.get("symbols_requested", []),
                "timeframe":                diag.get("timeframe", "5m"),
                "hypotheses_generated":     diag.get("hypotheses_generated", 0),
                "feasible_hypotheses":      diag.get("feasible_hypotheses", 0),
                "metrics_emitted":          funnel.get("metrics_emitted", 0),
                "pass_min_sample":          funnel.get("pass_min_sample_size", 0),
                "phase2_candidates_written": funnel.get("phase2_candidates_written", 0),
                "phase2_final":             funnel.get("phase2_final", 0),
                "multiplicity_discoveries": diag.get("multiplicity_discoveries", 0),
                "rejected_by_min_t":        diag.get("rejected_by_min_t_stat", 0),
                "rejected_invalid":         diag.get("rejected_invalid_metrics", 0),
                "rejection_reasons":        diag.get("rejection_reason_counts", {}),
                "min_t_stat":               diag.get("min_t_stat", 2.0),
                "event_families":           quality.get("event_families", []),
                "gate_pass_rate":           round(quality.get("gate_pass_rate", 0), 4),
                "search_parameterizations": burden.get("search_parameterizations_attempted", 0),
                "search_eligible":          burden.get("search_candidates_eligible", 0),
            })
        except Exception:
            continue
    return runs


def load_event_families(signals: list[dict]) -> list[dict]:
    best: dict[str, dict] = {}
    for s in signals:
        key = f"{s['category']}::{s['event']}"
        if key not in best or s["best_bps"] > best[key]["best_bps"]:
            best[key] = {**s, "key": key, "run_count": 0}
        best[key]["run_count"] = best[key].get("run_count", 0) + 1
    return sorted(best.values(), key=lambda x: x["best_bps"], reverse=True)


def load_event_specs() -> list[dict]:
    specs = []
    if not SPEC_EVENTS.exists():
        return specs
    for f in sorted(SPEC_EVENTS.glob("*.yaml")):
        d = _load_yaml(f)
        if not d or "event_type" not in d:
            continue
        g = d.get("governance", {})
        r = d.get("runtime", {})
        i = d.get("identity", {})
        specs.append({
            "name":             f.stem,
            "event_type":       d.get("event_type", f.stem),
            "phase":            i.get("phase", ""),
            "canonical_regime": i.get("canonical_regime", ""),
            "legacy_family":    i.get("legacy_family", ""),
            "tier":             g.get("tier", ""),
            "maturity":         g.get("maturity", ""),
            "executable":       g.get("default_executable", True),
            "research_only":    g.get("research_only", False),
            "enabled":          r.get("enabled", True),
            "detector":         r.get("detector", ""),
            "operational_role": g.get("operational_role", ""),
            "runtime_category": g.get("runtime_category", ""),
            "deployment_disposition": g.get("deployment_disposition", ""),
            "instrument_classes": r.get("instrument_classes", []),
            "runtime_tags":     r.get("runtime_tags", []),
        })
    return specs


def load_proposals() -> list[dict]:
    proposals = []
    if not SPEC_PROPOSALS.exists():
        return proposals
    for f in sorted(SPEC_PROPOSALS.glob("*.yaml")):
        d = _load_yaml(f)
        proposals.append({
            "filename": f.name,
            "path":     str(f.relative_to(ROOT)),
            "content":  d,
            "raw":      f.read_text(),
        })
    return proposals


def load_filter_templates() -> list[dict]:
    templates = []
    if not SPEC_TEMPLATES.exists():
        return templates
    for f in SPEC_TEMPLATES.glob("*.yaml"):
        d = _load_yaml(f)
        for k, v in d.items():
            if isinstance(v, dict):
                templates.append({"name": k, "source": f.name, **v})
    return templates


def load_theses() -> list[dict]:
    theses = []
    if not LIVE_THESES.exists():
        return theses
    for f in LIVE_THESES.rglob("promoted_theses.json"):
        try:
            data = _load_json(f)
            batch = data if isinstance(data, list) else data.get("theses", [])
            run_id = f.parent.name
            for t in batch:
                t["_run_id"] = run_id
                theses.append(t)
        except Exception:
            continue
    return theses


def load_lake() -> dict:
    if not LAKE_DIR.exists():
        return {"run_caches": [], "cleaned_symbols": [], "feature_symbols": []}

    run_caches = []
    runs_dir = LAKE_DIR / "runs"
    if runs_dir.exists():
        for d in sorted(runs_dir.iterdir()):
            if d.is_dir():
                n_files = sum(1 for _ in d.rglob("*.parquet"))
                size_mb = sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) / 1e6
                run_caches.append({
                    "name": d.name,
                    "parquet_files": n_files,
                    "size_mb": round(size_mb, 1),
                })

    cleaned_syms = []
    cleaned_dir = LAKE_DIR / "cleaned" / "perp"
    if cleaned_dir.exists():
        for sym_dir in sorted(cleaned_dir.iterdir()):
            if sym_dir.is_dir():
                bars  = list(sym_dir.rglob("*.parquet"))
                years = sorted({p.parent.parent.name.replace("year=", "") for p in bars if "year=" in str(p)})
                cleaned_syms.append({"symbol": sym_dir.name, "bars_files": len(bars), "years": years})

    feature_syms = []
    feat_dir = LAKE_DIR / "features" / "perp"
    if feat_dir.exists():
        for sym_dir in sorted(feat_dir.iterdir()):
            if sym_dir.is_dir():
                feature_syms.append({
                    "symbol": sym_dir.name,
                    "feature_types": [d.name for d in sym_dir.iterdir() if d.is_dir()],
                })

    return {"run_caches": run_caches, "cleaned_symbols": cleaned_syms, "feature_symbols": feature_syms}


def load_templates() -> dict:
    """Load spec/templates/registry.yaml — families, expression/filter templates, param grids."""
    d = _load_yaml(SPEC_TEMPLATES / "registry.yaml")
    if not d:
        return {"families": [], "defaults": {}}

    defaults = d.get("defaults", {})
    families: list[dict] = []

    for key, val in d.items():
        if key in ("version", "kind", "metadata", "defaults") or not isinstance(val, dict):
            continue
        templates_list: list[dict] = []
        for tname, tval in val.items():
            if isinstance(tval, dict):
                templates_list.append({"name": tname, **tval})
        families.append({
            "name":      key,
            "templates": templates_list,
        })

    return {"families": families, "defaults": defaults}


def load_features() -> list[dict]:
    """Load project/configs/registries/features.yaml."""
    d = _load_yaml(FEATURES_YAML)
    features = []
    for name, props in d.get("features", {}).items():
        if isinstance(props, dict):
            features.append({"name": name, **props})
    return features


def load_live_state() -> dict:
    """Load live/persist/ files."""
    recon = _load_json(LIVE_PERSIST / "thesis_reconciliation.json") if LIVE_PERSIST.exists() else {}
    batch = _load_json(LIVE_PERSIST / "thesis_batch_metadata.json") if LIVE_PERSIST.exists() else {}
    memories: list[dict] = []
    if ARTIFACTS_DIR.exists():
        for campaign_dir in sorted(ARTIFACTS_DIR.iterdir()):
            if campaign_dir.is_dir():
                mem_dir = campaign_dir / "memory"
                belief  = _load_json(mem_dir / "belief_state.json") if mem_dir.exists() else {}
                actions = _load_json(mem_dir / "next_actions.json") if mem_dir.exists() else {}
                memories.append({
                    "campaign":    campaign_dir.name,
                    "belief":      belief,
                    "next_actions": actions,
                })
    return {
        "reconciliation": recon,
        "batch_metadata": batch,
        "campaign_memories": memories,
    }


def load_domain_graph_summary() -> dict:
    """Load spec/domain/domain_graph.yaml and return a lightweight summary."""
    d = _load_yaml(SPEC_DOMAIN)
    if not d:
        return {"events": [], "families": [], "regimes": []}

    events: list[dict] = []
    raw_events = d.get("events", d.get("event_nodes", {}))
    if isinstance(raw_events, dict):
        for ename, edata in raw_events.items():
            if isinstance(edata, dict):
                events.append({
                    "name":             ename,
                    "research_family":  edata.get("research_family", ""),
                    "canonical_regime": edata.get("canonical_regime", ""),
                    "detector_name":    edata.get("detector_name", ""),
                    "tier":             edata.get("tier", ""),
                    "templates":        edata.get("templates", []),
                    "horizons":         edata.get("horizons", []),
                    "phase":            edata.get("phase", ""),
                })
    elif isinstance(raw_events, list):
        for edata in raw_events:
            if isinstance(edata, dict):
                name = edata.get("event_type", edata.get("name", ""))
                events.append({
                    "name":             name,
                    "research_family":  edata.get("research_family", ""),
                    "canonical_regime": edata.get("canonical_regime", ""),
                    "detector_name":    edata.get("detector_name", ""),
                    "tier":             edata.get("tier", ""),
                    "templates":        edata.get("templates", []),
                    "horizons":         edata.get("horizons", []),
                    "phase":            edata.get("phase", ""),
                })

    # Collect unique families and regimes
    families = sorted({e["research_family"] for e in events if e["research_family"]})
    regimes  = sorted({e["canonical_regime"] for e in events if e["canonical_regime"]})

    return {"events": events, "families": families, "regimes": regimes}


CAMPAIGNS = [
    {
        "id": "liquidation_cascade_proxy",
        "name": "LIQUIDATION_CASCADE_PROXY",
        "status": "stopped",
        "decision": "STOP",
        "reason": "t ceiling ~1.8, gate requires 2.0. Proxy fires on OI+volume coincidences including false positives.",
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "date_range": "2021–2024",
        "best_run": "liq_proxy_combined",
        "stats": [
            {"label": "Best t-stat BTC", "value": "1.73"},
            {"label": "Best t-stat ETH", "value": "1.79"},
            {"label": "Best horizon",    "value": "60m long"},
            {"label": "Mean bps BTC",    "value": "10.1"},
            {"label": "Mean bps ETH",    "value": "12.5"},
            {"label": "t-stat gate",     "value": "≥ 2.0"},
        ],
        "config": "oi_drop_quantile=0.98, vol_surge_quantile=0.90",
        "watchlist": "Revisit with cleaner OI source or cross-asset confirmation.",
    },
    {
        "id": "funding_extreme_onset",
        "name": "FUNDING_EXTREME_ONSET",
        "status": "stopped",
        "decision": "STOP",
        "reason": "Robustness ceiling ~0.527 across all single-feature conditioning. Gate requires 0.6. Signal is real but structurally regime-inconsistent.",
        "symbols": ["BTCUSDT"],
        "date_range": "2021–2024",
        "best_run": "funding_extreme_combined",
        "stats": [
            {"label": "Best t-stat",    "value": "3.35"},
            {"label": "Best filter",    "value": "only_if_highvol"},
            {"label": "Best robustness","value": "0.527"},
            {"label": "Robustness gate","value": "≥ 0.600"},
            {"label": "Horizon",        "value": "60m long"},
            {"label": "ETH signal",     "value": "None"},
        ],
        "conditioning": [
            {"filter": "only_if_regime (rv>0.70)", "n": 671, "t_stat": 3.31, "robustness": 0.527},
            {"filter": "only_if_highvol (rv>0.85)","n": 667, "t_stat": 3.35, "robustness": 0.519},
            {"filter": "unconditional",             "n": 684, "t_stat": 3.27, "robustness": 0.475},
            {"filter": "only_if_trend",             "n": 135, "t_stat": 2.17, "robustness": 0.514},
            {"filter": "only_if_funding",           "n": 532, "t_stat": 2.88, "robustness": 0.471},
            {"filter": "only_if_oi",                "n": 402, "t_stat": 2.71, "robustness": 0.402},
        ],
        "watchlist": "Revisit if multi-feature regime classifier available, or with cross-asset confirmation.",
    },
    {
        "id": "all_events_systematic",
        "name": "ALL-EVENTS SYSTEMATIC",
        "status": "active",
        "decision": "ONGOING",
        "reason": "Systematic tuning of all events across 7 batches. CLIMAX_VOLUME_BAR best robustness found so far (rob=0.6813, passes gate).",
        "symbols": ["BTCUSDT", "ETHUSDT"],
        "date_range": "2021–2024",
        "best_run": "climax_regime",
        "stats": [
            {"label": "Best event",     "value": "CLIMAX_VOLUME_BAR"},
            {"label": "Best robustness","value": "0.6813"},
            {"label": "Batches run",    "value": "7"},
            {"label": "Robustness gate","value": "≥ 0.600"},
            {"label": "BASIS_DISLOC",   "value": "Blocked (no spot data)"},
            {"label": "Batch 8",        "value": "Next"},
        ],
        "watchlist": "Need spot data for basis/spot-perp family. Batch 8 up next.",
    },
]


def load_overview(signals, runs, events) -> dict:
    total_hyp   = sum(r.get("hypotheses_generated", 0) for r in runs)
    total_cands = sum(r.get("phase2_candidates_written", 0) for r in runs)
    total_met   = sum(r.get("metrics_emitted", 0) for r in runs)
    best        = signals[0] if signals else {}
    cat_counts: dict[str, int] = {}
    for s in signals:
        cat_counts[s["category"]] = cat_counts.get(s["category"], 0) + 1
    return {
        "total_runs":               len(runs),
        "total_signals":            len(signals),
        "total_hypotheses":         total_hyp,
        "total_events_tested":      total_met,
        "total_candidates_written": total_cands,
        "total_event_families":     len(events),
        "best_signal_bps":          best.get("best_bps", 0),
        "best_signal_event":        best.get("event", ""),
        "best_signal_run":          best.get("run", ""),
        "campaigns_stopped":        2,
        "campaigns_active":         1,
        "funnel": {
            "hypotheses":        total_hyp,
            "feasible":          sum(r.get("feasible_hypotheses", 0) for r in runs),
            "metrics_emitted":   total_met,
            "min_sample_pass":   sum(r.get("pass_min_sample", 0) for r in runs),
            "candidates_written": total_cands,
        },
        "category_counts": cat_counts,
        "top_signals": signals[:10],
    }


def save_proposal(filename: str, content: str) -> dict:
    SPEC_PROPOSALS.mkdir(parents=True, exist_ok=True)
    if not filename.endswith(".yaml"):
        filename += ".yaml"
    safe = "".join(c if c.isalnum() or c in "_-." else "_" for c in filename)
    target = SPEC_PROPOSALS / safe
    target.write_text(content)
    return {"ok": True, "path": str(target.relative_to(ROOT)), "filename": safe}


# ─── HTTP Handler ─────────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    _data: dict = {}

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")

    def send_json(self, data, status: int = 200):
        body = json.dumps(data, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: pathlib.Path, ctype: str):
        try:
            body = path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except FileNotFoundError:
            self.send_response(404); self.end_headers()

    def read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        qs     = parse_qs(parsed.query)
        d      = self._data

        if path in ("/", "/index.html"):
            self.send_file(STATIC / "index.html", "text/html; charset=utf-8")
            return

        # Job log streaming
        if path.startswith("/api/jobs/") and path.endswith("/log"):
            job_id = path.split("/")[3]
            job = JOBS.get(job_id)
            if not job:
                self.send_json({"error": "not found"}, 404); return
            log_path = pathlib.Path(job["log_path"])
            offset = int(qs.get("offset", ["0"])[0])
            try:
                text = log_path.read_text(errors="replace")
                self.send_json({"text": text[offset:], "size": len(text), "status": job["status"]})
            except FileNotFoundError:
                self.send_json({"text": "", "size": 0, "status": job["status"]})
            return

        routes = {
            "/api/overview":      lambda: d["overview"],
            "/api/signals":       lambda: self._filter_signals(d["signals"], qs),
            "/api/runs":          lambda: self._get_runs(d["runs"], qs),
            "/api/events":        lambda: d["events"],
            "/api/event-specs":   lambda: d["event_specs"],
            "/api/campaigns":     lambda: CAMPAIGNS,
            "/api/lake":          lambda: d["lake"],
            "/api/proposals":     lambda: load_proposals(),
            "/api/theses":        lambda: load_theses(),
            "/api/signal":        lambda: self._get_signal(d["signals"], qs),
            "/api/jobs":          lambda: list(JOBS.values()),
            "/api/templates":     lambda: load_templates(),
            "/api/features":      lambda: load_features(),
            "/api/live-state":    lambda: load_live_state(),
            "/api/domain-graph":  lambda: load_domain_graph_summary(),
        }

        handler = routes.get(path)
        if handler:
            try:
                self.send_json(handler())
            except Exception as e:
                self.send_json({"error": str(e)}, 500)
        else:
            self.send_response(404); self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        if path == "/api/proposals/save":
            try:
                body = json.loads(self.read_body())
                result = save_proposal(body.get("filename", "proposal"), body.get("content", ""))
                self.send_json(result)
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 400)
            return

        if path == "/api/run":
            try:
                body   = json.loads(self.read_body())
                stage  = body.get("stage", "discover")
                subcmd = body.get("subcmd", "run")
                args   = body.get("args", {})

                if stage == "discover" and subcmd == "run":
                    proposal = args.get("proposal", "")
                    run_id   = args.get("run_id", "")
                    if not proposal:
                        self.send_json({"ok": False, "error": "proposal required"}, 400); return
                    cmd = ["python3", "-m", "project.cli", "discover", "run",
                           "--proposal", proposal]
                    if run_id:
                        cmd += ["--run_id", run_id]
                    label = f"discover·{run_id or proposal}"

                elif stage == "discover" and subcmd == "plan":
                    proposal = args.get("proposal", "")
                    if not proposal:
                        self.send_json({"ok": False, "error": "proposal required"}, 400); return
                    cmd = ["python3", "-m", "project.cli", "discover", "plan",
                           "--proposal", proposal]
                    label = f"plan·{proposal}"

                elif stage == "validate":
                    run_id = args.get("run_id", "")
                    if not run_id:
                        self.send_json({"ok": False, "error": "run_id required"}, 400); return
                    cmd = ["python3", "-m", "project.cli", "validate", "run", "--run_id", run_id]
                    label = f"validate·{run_id}"

                elif stage == "promote":
                    run_id  = args.get("run_id", "")
                    symbols = args.get("symbols", "BTCUSDT,ETHUSDT")
                    if not run_id:
                        self.send_json({"ok": False, "error": "run_id required"}, 400); return
                    cmd = ["python3", "-m", "project.cli", "promote", "run",
                           "--run_id", run_id, "--symbols", symbols]
                    label = f"promote·{run_id}"

                elif stage == "ingest":
                    run_id  = args.get("run_id", "")
                    symbols = args.get("symbols", "BTCUSDT,ETHUSDT")
                    start   = args.get("start", "2021-01-01")
                    end     = args.get("end", "2024-12-31")
                    cmd = ["python3", "-m", "project.cli", "ingest",
                           "--run_id", run_id, "--symbols", symbols,
                           "--start", start, "--end", end]
                    label = f"ingest·{run_id}"

                elif stage == "build-graph":
                    cmd = ["python3", "project/scripts/build_domain_graph.py"]
                    label = "build-graph"

                else:
                    self.send_json({"ok": False, "error": f"unknown stage: {stage}"}, 400)
                    return

                job = start_job(cmd, label)
                self.send_json({"ok": True, "job": job})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 400)
            return

        if path == "/api/reload":
            try:
                self._data.update(self._reload_data())
                self.send_json({"ok": True, "reloaded_at": datetime.datetime.now().isoformat()})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)}, 500)
            return

        self.send_response(404); self.end_headers()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _filter_signals(self, sigs, qs):
        sym   = qs.get("symbol",   [None])[0]
        cat   = qs.get("category", [None])[0]
        min_b = float(qs.get("min_bps", ["-999"])[0])
        q     = (qs.get("q", [""])[0] or "").lower()
        if sym:   sigs = [s for s in sigs if sym in s.get("by_symbol", {})]
        if cat:   sigs = [s for s in sigs if s["category"] == cat]
        if min_b != -999: sigs = [s for s in sigs if s["best_bps"] >= min_b]
        if q:     sigs = [s for s in sigs if q in s["event"].lower() or q in s["category"].lower()]
        return sigs

    def _get_runs(self, runs, qs):
        run_id = qs.get("id", [None])[0]
        if run_id:
            return next((r for r in runs if r["run_id"] == run_id), {})
        return runs

    def _get_signal(self, sigs, qs):
        sig_id = qs.get("id", [None])[0]
        return next((s for s in sigs if s["id"] == sig_id), {}) if sig_id else {}

    @staticmethod
    def _reload_data() -> dict:
        signals = load_signals()
        runs    = load_runs()
        events  = load_event_families(signals)
        return {
            "signals":     signals,
            "runs":        runs,
            "events":      events,
            "lake":        load_lake(),
            "event_specs": load_event_specs(),
            "overview":    load_overview(signals, runs, events),
        }


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7477

    print("Edge Research Platform")
    print("=" * 44)
    print("Loading data...")

    data = Handler._reload_data()
    Handler._data = data

    print(f"  Signals:      {len(data['signals'])}")
    print(f"  Runs:         {len(data['runs'])}")
    print(f"  Events:       {len(data['events'])}")
    print(f"  Event specs:  {len(data['event_specs'])}")
    print(f"  Lake caches:  {len(data['lake']['run_caches'])}")
    print(f"  Best signal:  {data['overview']['best_signal_event']} "
          f"@ {data['overview']['best_signal_bps']} bps")

    httpd = HTTPServer(("", port), Handler)
    print()
    print(f"  Platform → http://localhost:{port}")
    print("  Ctrl+C to stop")
    print()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n  Stopped.")


if __name__ == "__main__":
    main()
