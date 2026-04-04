from dataclasses import dataclass

@dataclass(frozen=True)
class DiscoveryBenchmarkMode:
    name: str
    enable_v2: bool
    enable_ledger: bool

LEGACY = DiscoveryBenchmarkMode("legacy", enable_v2=False, enable_ledger=False)
V2 = DiscoveryBenchmarkMode("v2", enable_v2=True, enable_ledger=False)
LEDGER = DiscoveryBenchmarkMode("ledger", enable_v2=True, enable_ledger=True)
