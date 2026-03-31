# Proposal Compilation Template

Use this template when compiling a mechanism hypothesis into a proposal.

## 1. Source Hypothesis

| Field | Value |
|-------|-------|
| hypothesis_id | |
| version | |
| parent_run_id | |
| canonical_regime | |
| event_family | |

## 2. Pre-Compilation Validation

### Event Validation
| Event | In canonical_event_registry.yaml? | Family |
|-------|-----------------------------------|--------|
| | yes/no | |

### Template Validation
| Template | In event_template_registry.yaml for family? |
|----------|---------------------------------------------|
| | yes/no |

### Horizon Validation
| Horizon (bars) | Supported for timeframe? | Maps to |
|----------------|--------------------------|---------|
| | yes/no | |

### Regime Validation
| Regime | In regime_routing.yaml? |
|--------|-------------------------|
| | yes/no |

## 3. Compiled Proposal YAML

```yaml
<proposal YAML>
```

## 4. Commands

### Translation
```bash
<command>
```

### Plan Only
```bash
<command>
```

### Execution
```bash
<command>
```

## 5. Plan Review Checklist

- [ ] program_id correct
- [ ] symbols valid
- [ ] dates valid and reasonable
- [ ] timeframe supported
- [ ] horizons_bars supported
- [ ] templates valid for event family
- [ ] events in canonical registry
- [ ] regime in routing table
- [ ] directions valid
- [ ] entry_lags >= 1
- [ ] promotion_profile valid
- [ ] search_control within limits
- [ ] no forbidden knobs
- [ ] YAML parses cleanly

## 6. Translation Verification

```
<output of translation command>
```

## 7. Plan Verification

```
<output of plan-only command>
```

## 8. Coordinator Sign-Off

- [ ] All validation passed
- [ ] Translation succeeded
- [ ] Plan succeeded
- [ ] Ready for user approval
