# Handoff: Compiler -> Coordinator

## Context

The compiler has completed proposal compilation. The coordinator should now:

1. Review the plan review checklist
2. Run the translation command to validate
3. Run the plan-only command to verify
4. Present to the user for approval before execution

## Compiled Output

### Proposal Path
{{proposal_path}}

### Proposal YAML
```yaml
{{proposal_yaml}}
```

### Translation Command
```bash
{{translation_command}}
```

### Plan-Only Command
```bash
{{plan_only_command}}
```

### Execution Command
```bash
{{execution_command}}
```

### Plan Review Checklist
{{plan_review_checklist}}

### Validation Notes
{{validation_notes}}

## Coordinator Action Required

- [ ] Review checklist items
- [ ] Run translation command
- [ ] Run plan-only command
- [ ] Review validated plan output
- [ ] Present to user for approval
- [ ] On approval: run execution command
- [ ] After execution: invoke analyst on new run_id
