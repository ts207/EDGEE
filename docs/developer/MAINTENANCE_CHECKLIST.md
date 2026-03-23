# Maintenance Checklist

Use this checklist when changing a contract, surface, or generated artifact.

## Contracts and generated docs

- Update schemas in `project/contracts/` if the data shape changed.
- Update the corresponding tests.
- Update `docs/CURRENT_STATE_AND_GAPS.md` if the change alters the supported surface.
- Update any role doc that explains the changed workflow.

## Research and orchestration

If the change touches campaign control, memory, frontier ordering, or promotion:

- Review `project/pipelines/research/campaign_controller.py`
- Review `project/pipelines/research/update_campaign_memory.py`
- Review `project/pipelines/research/search_intelligence.py`
- Review `project/research/knowledge/`
- Review `project/research/services/`

## Strategy and live handoff

If the change affects promotion, blueprinting, allocation, or execution:

- Review `project/research/promotion/`
- Review `project/pipelines/research/compile_strategy_blueprints.py`
- Review `project/portfolio/`
- Review `project/live/`

## Search surface changes

If the change adds or removes search scope:

- Update `spec/search_space.yaml`
- Update registry and validator tests
- Confirm the campaign controller proposal logic still respects the intended frontier order
- Confirm the memory and promotion docs still match actual behavior

## Architecture and surface maintenance

- Keep package-root boundaries stable.
- Keep compatibility facades thin.
- Remove or rename obsolete paths only with explicit doc updates.

## Verification order

1. Smallest unit test that exercises the changed contract.
2. Focused pipeline or service test.
3. Broader smoke or integration check.
4. Documentation pass.

## Research calibration

When changing synthetic calibration or benchmark logic:

- Update the maintained benchmark guide.
- Verify the calibration path still produces the expected truth artifacts.
- Check that synthetic results are not being described as live evidence.

## Red flags

- A file writes a field that no consumer reads.
- A consumer reads a field that no producer writes.
- A doc claims a capability that the code does not expose.
- A change only works because old behavior is still implicitly tolerated.
