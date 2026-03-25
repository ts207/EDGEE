from __future__ import annotations
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from project.strategy.dsl.templates import TemplateRegistry, TemplateSpec, TemplateParameter
from project.core.exceptions import ConfigurationError

def test_template_registry_load_and_get():
    mock_registry = MagicMock()
    mock_registry.searchable_event_families = ["VOL_SHOCK", "LIQUIDITY_DISLOCATION"]
    mock_registry.family_templates.side_effect = lambda family: ["reversal", "breakout"] if family == "VOL_SHOCK" else ["extreme"]

    with patch("project.strategy.dsl.templates.get_domain_registry", return_value=mock_registry):
        TemplateRegistry.load_from_yaml()
        
        templates = TemplateRegistry.list_templates()
        assert "vol_shock_reversal" in templates
        assert "vol_shock_breakout" in templates
        assert "liquidity_dislocation_extreme" in templates
        
        spec = TemplateRegistry.get_template("VOL_SHOCK", "reversal")
        assert spec is not None
        assert spec.name == "reversal"
        assert spec.family == "VOL_SHOCK"
        
        spec = TemplateRegistry.get_template("NON_EXISTENT", "template")
        assert spec is None

def test_template_registry_error():
    with patch("project.strategy.dsl.templates.get_domain_registry", side_effect=RuntimeError("Mock error")):
        with pytest.raises(ConfigurationError):
            TemplateRegistry.load_from_yaml()

def test_template_parameter_and_spec_models():
    param = TemplateParameter(name="p1", type="float", default=1.0, description="desc")
    assert param.name == "p1"
    assert param.default == 1.0
    
    spec = TemplateSpec(name="t1", family="f1", parameters=[param])
    assert spec.name == "t1"
    assert len(spec.parameters) == 1
    assert spec.default_exit_bars == 48
