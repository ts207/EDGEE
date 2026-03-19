"""
Tests that confirm the explicit no-op semantics of oos_validation_pass
and that the legacy name raises an error so production blueprints cannot
silently rely on a phantom safety surface.
"""

import pandas as pd
import pytest
from unittest.mock import MagicMock


def _make_frame(n: int = 5) -> pd.DataFrame:
    return pd.DataFrame({"spread_abs": [0.5] * n, "funding_bps_abs": [1.0] * n})


def _make_blueprint() -> MagicMock:
    bp = MagicMock()
    bp.id = "test_bp"
    bp.overlays = []
    return bp


def test_oos_validation_pass_raises_unknown_signal():
    """The legacy oos_validation_pass signal must not silently pass.
    Production blueprints referencing it should fail at evaluation time.
    """
    from project.strategy.runtime.dsl_runtime.signal_resolution import signal_mask

    frame = _make_frame()
    bp = _make_blueprint()
    with pytest.raises(ValueError, match="unknown trigger signals"):
        signal_mask(signal="oos_validation_pass", frame=frame, blueprint=bp)


def test_event_detected_returns_false_when_column_absent():
    """event_detected must return an all-False mask when the column is absent.

    The original bug was returning True unconditionally (all bars trigger = bypassed event
    detection). The correct behaviour when no event_detected column exists in the frame is
    False for every row — no events means no triggers, not a free pass.
    """
    from project.strategy.runtime.dsl_runtime.signal_resolution import signal_mask

    frame = _make_frame()
    bp = _make_blueprint()
    result = signal_mask(signal="event_detected", frame=frame, blueprint=bp)
    assert not result.any(), (
        "event_detected with no column must return all-False, not silently trigger entries"
    )
