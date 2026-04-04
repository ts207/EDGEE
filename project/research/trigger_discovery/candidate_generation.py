from __future__ import annotations

import logging
import itertools
from typing import Dict, List, Any, Tuple

import pandas as pd
import numpy as np

from project.domain.hypotheses import HypothesisSpec, TriggerSpec
from project.research.trigger_discovery.candidate_clustering import extract_excursions, cluster_excursions

log = logging.getLogger(__name__)

class TriggerProposal:
    """Wrapper that tracks a mined candidate trigger along with its metadata."""
    def __init__(
        self,
        candidate_trigger_id: str,
        source_lane: str,
        detector_family: str,
        parameterization: Dict[str, Any],
        dominant_features: List[str] = None,
        suggested_trigger_name: str = "",
        spec: HypothesisSpec = None,
    ):
        self.candidate_trigger_id = candidate_trigger_id
        self.source_lane = source_lane
        self.detector_family = detector_family
        self.parameterization = parameterization
        self.dominant_features = dominant_features or []
        self.suggested_trigger_name = suggested_trigger_name
        self.spec = spec


def generate_parameter_sweep(
    features: pd.DataFrame,
    family_grid: Dict[str, Dict[str, List[float]]],
    base_template_id: str = "continuation",
    base_direction: str = "long",
    base_horizon: str = "12b"
) -> Tuple[List[TriggerProposal], pd.DataFrame]:
    """
    Lane A: Given a feature table, generate parameterized threshold masks 
    for known detector proxies (e.g. vol_shock proxy), returning the proposals
    and a MUTATED features dataframe with new boolean trigger columns injected.
    """
    if features.empty:
        return [], features

    proposals = []
    out_features = features.copy()
    
    # We construct pseudo-detectors directly against raw numeric columns
    # Example family: "vol_shock" mapping to testing thresholds over "realized_vol"
    
    for family, grid in family_grid.items():
        if family == "vol_shock":
            base_col = next((c for c in features.columns if "rv" in c.lower() or "vol" in c.lower() and "shock" not in c.lower()), None)
            if not base_col:
                log.warning("No realized volatility proxy feature found for vol_shock sweep")
                continue
                
            thresholds = grid.get("z_threshold", [2.0])
            for count, z in enumerate(thresholds):
                pseudo_event_id = f"PROPOSED_VOL_SHOCK_Z{str(z).replace('.', 'p')}"
                mask_col = f"{pseudo_event_id.upper()}_EVENT"
                
                # Approximate dynamic threshold logic
                series = pd.to_numeric(out_features[base_col], errors="coerce").fillna(0.0)
                rm = series.rolling(288, min_periods=20).mean()
                rs = series.rolling(288, min_periods=20).std().replace(0, 1e-9)
                z_series = (series - rm) / rs
                
                # Onset crossing
                onset = (z_series >= z) & (z_series.shift(1, fill_value=0.0) < z)
                out_features[mask_col] = onset.fillna(False).astype(bool)
                
                # Create spec that just targets the new column implicitly using feature predicate
                # Actually, since it's a new boolean column, we can use a FEATURE_PREDICATE directly
                # on the generated mask_col == 1.
                spec = HypothesisSpec(
                    trigger=TriggerSpec.feature_predicate(feature=mask_col, operator="==", threshold=1.0),
                    direction=base_direction,
                    horizon=base_horizon,
                    template_id=base_template_id
                )
                
                prop = TriggerProposal(
                    candidate_trigger_id=f"cand_{pseudo_event_id.lower()}",
                    source_lane="parameter_sweep",
                    detector_family=family,
                    parameterization={"z_threshold": z},
                    suggested_trigger_name=pseudo_event_id,
                    spec=spec
                )
                proposals.append(prop)

    return proposals, out_features


def generate_feature_clusters(
    features: pd.DataFrame,
    target_columns: List[str],
    min_support: int = 5,
    base_template_id: str = "continuation",
    base_direction: str = "long",
    base_horizon: str = "12b"
) -> Tuple[List[TriggerProposal], pd.DataFrame]:
    """
    Lane B: Mine excursions from arbitrary target feature columns and cluster them.
    """
    if features.empty or not target_columns:
        return [], features

    out_features = features.copy()
    
    excursions_df = extract_excursions(features, target_columns, threshold_z=2.5, min_persistence=1)
    if excursions_df.empty:
        return [], out_features
        
    clusters = cluster_excursions(excursions_df, target_columns, min_support=min_support)
    
    proposals = []
    
    for clst in clusters:
        candidate_trigger_id = clst["candidate_cluster_id"]
        dom = clst["dominant_features"]
        suggested_name = clst["suggested_trigger_family"]
        
        # Build the intersection mask for this cluster
        mask_col = f"PROPOSED_{candidate_trigger_id.upper()}_EVENT"
        mask = excursions_df[dom].all(axis=1)
        out_features[mask_col] = mask.astype(bool)
        
        spec = HypothesisSpec(
            trigger=TriggerSpec.feature_predicate(feature=mask_col, operator="==", threshold=1.0),
            direction=base_direction,
            horizon=base_horizon,
            template_id=base_template_id
        )
        
        prop = TriggerProposal(
            candidate_trigger_id=candidate_trigger_id,
            source_lane="feature_cluster",
            detector_family="excursion_cluster",
            parameterization={"source_columns": dom, "threshold_z": 2.5},
            dominant_features=dom,
            suggested_trigger_name=suggested_name,
            spec=spec
        )
        proposals.append(prop)
        
    return proposals, out_features
