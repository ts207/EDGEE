import pandas as pd
import pytest
from project.events.detectors.sequence import EventSequenceDetector
from unittest.mock import MagicMock, patch

def test_event_sequence_detector_basic():
    # Mock load_ontology_events to return a spec for our test event
    mock_spec = {
        "parameters": {
            "anchor_event": "E1",
            "trigger_event": "E2",
            "max_gap_bars": 2
        }
    }
    
    with patch("project.events.detectors.sequence.load_ontology_events", return_value={"SEQ_E1_E2": mock_spec}):
        with patch("project.events.detectors.sequence.get_detector") as mock_get_detector:
            # Mock anchor detector
            anchor_det = MagicMock()
            anchor_det.prepare_features.return_value = {"f1": pd.Series([0, 0, 0, 0])}
            anchor_det.compute_raw_mask.return_value = pd.Series([True, False, False, False])
            
            # Mock trigger detector
            trigger_det = MagicMock()
            trigger_det.prepare_features.return_value = {"f2": pd.Series([0, 0, 0, 0])}
            trigger_det.compute_raw_mask.return_value = pd.Series([False, True, False, False])
            
            def side_effect(name):
                if name == "E1": return anchor_det
                if name == "E2": return trigger_det
                return None
            mock_get_detector.side_effect = side_effect
            
            det = EventSequenceDetector()
            det.event_type = "SEQ_E1_E2"
            
            df = pd.DataFrame({"timestamp": pd.date_range("2024-01-01", periods=4, freq="5min")})
            
            # compute_raw_mask is what EventSequenceDetector implements
            features = det.prepare_features(df)
            mask = det.compute_raw_mask(df, features=features)
            
            assert mask.iloc[1] == True
            assert mask.sum() == 1
