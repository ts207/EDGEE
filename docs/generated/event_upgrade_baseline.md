# Event upgrade baseline

- Baseline active events: `70`
- Post-upgrade active events: `70`
- Baseline registered detectors: `70`
- Post-upgrade registered detectors: `70`
- Baseline registry entries: `78`
- Post-upgrade registry entries: `72`
- Baseline detector issues: `7`
- Post-upgrade detector issues: `0`
- Baseline ontology issues: `0`
- Post-upgrade ontology issues: `0`
- Baseline default executable events: `61`
- Post-upgrade default executable events: `61`

## Active set delta

- Added: None
- Removed: None

## Notable changes

- load_ontology_events now resolves from the authoritative unified registry instead of directory scanning
- INT_* research motifs no longer register into the default runtime detector set
- CROSS_ASSET_DESYNC_EVENT now requires paired data and emits no degraded single-asset fallback
- FUNDING_EXTREME_ONSET now requires acceleration plus persistence before onset emission
- CROSS_VENUE_DESYNC now emits episode onset once per shock/reversion cycle
- Duplicate exhaustion detector class shadowing and duplicated FundingTimestampDetector.prepare_features were removed
- Event contract normalization, tiers, and maturity matrix artifacts were added for all active events
