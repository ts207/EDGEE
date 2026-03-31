from __future__ import annotations

from project.research.run_hypothesis_search import _make_parser, _resolve_search_min_t_stat


def test_run_hypothesis_search_parser_defaults_min_t_stat_to_none() -> None:
    parser = _make_parser()
    args = parser.parse_args(["--run_id", "r1", "--symbols", "BTCUSDT"])
    assert args.min_t_stat is None


def test_run_hypothesis_search_uses_gate_default_when_cli_omitted() -> None:
    assert _resolve_search_min_t_stat(None) == 1.5


def test_run_hypothesis_search_preserves_explicit_min_t_stat_override() -> None:
    assert _resolve_search_min_t_stat(2.25) == 2.25
