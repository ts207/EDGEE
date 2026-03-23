"""
Live Kill-Switch and Unwind Orchestration.

Monitors drift and account health to trigger automated de-risking (kill-switches)
and position unwinding.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Callable

from project.live.health_checks import evaluate_pretrade_microstructure_gate
from project.live.state import LiveStateStore

LOGGER = logging.getLogger(__name__)


class KillSwitchReason(Enum):
    FEATURE_DRIFT = auto()
    EXECUTION_DRIFT = auto()
    EXCESSIVE_DRAWDOWN = auto()
    EXCHANGE_DISCONNECT = auto()
    STALE_DATA = auto()
    MICROSTRUCTURE_BREAKDOWN = auto()
    ACCOUNT_SYNC_LOSS = auto()
    MANUAL = auto()


@dataclass
class KillSwitchStatus:
    is_active: bool = False
    reason: Optional[KillSwitchReason] = None
    triggered_at: Optional[datetime] = None
    message: str = ""
    recovery_streak: int = 0
    peak_equity: float = 0.0


class KillSwitchManager:
    def __init__(self, state_store: LiveStateStore, *, microstructure_recovery_streak: int = 3):
        self.state_store = state_store
        self.status = KillSwitchStatus()
        self._on_trigger_callbacks: List[Callable[[KillSwitchReason, str], None]] = []
        self.microstructure_recovery_streak = max(1, int(microstructure_recovery_streak))
        self._load_persisted_status()

    def register_callback(self, callback: Callable[[KillSwitchReason, str], None]):
        self._on_trigger_callbacks.append(callback)

    def _serialize_status(self) -> Dict[str, Any]:
        return {
            "is_active": bool(self.status.is_active),
            "reason": self.status.reason.name if self.status.reason is not None else None,
            "triggered_at": self.status.triggered_at.isoformat()
            if self.status.triggered_at
            else None,
            "message": str(self.status.message),
            "recovery_streak": int(self.status.recovery_streak),
            "peak_equity": float(self.status.peak_equity),
        }

    def _persist_status(self) -> None:
        self.state_store.set_kill_switch_snapshot(self._serialize_status())

    def _load_persisted_status(self) -> None:
        snapshot = self.state_store.get_kill_switch_snapshot()
        reason_name = snapshot.get("reason")
        reason = None
        if reason_name:
            try:
                reason = KillSwitchReason[str(reason_name)]
            except KeyError:
                LOGGER.warning("Unknown persisted kill-switch reason %r; ignoring.", reason_name)
        triggered_at_raw = snapshot.get("triggered_at")
        triggered_at = None
        if triggered_at_raw:
            try:
                triggered_at = datetime.fromisoformat(str(triggered_at_raw))
            except ValueError:
                LOGGER.warning(
                    "Invalid persisted kill-switch timestamp %r; ignoring.", triggered_at_raw
                )
        self.status = KillSwitchStatus(
            is_active=bool(snapshot.get("is_active", False)),
            reason=reason,
            triggered_at=triggered_at,
            message=str(snapshot.get("message", "")),
            recovery_streak=int(snapshot.get("recovery_streak", 0) or 0),
            peak_equity=float(snapshot.get("peak_equity", 0.0)),
        )

    def trigger(self, reason: KillSwitchReason, message: str = ""):
        if self.status.is_active:
            return

        self.status = KillSwitchStatus(
            is_active=True,
            reason=reason,
            triggered_at=datetime.now(timezone.utc),
            message=message,
            recovery_streak=0,
        )
        self._persist_status()
        LOGGER.critical(f"KILL-SWITCH TRIGGERED: {reason.name} - {message}")

        for cb in self._on_trigger_callbacks:
            try:
                cb(reason, message)
            except Exception as e:
                LOGGER.error(f"Error in kill-switch callback: {e}")

    def reset(self):
        self.status = KillSwitchStatus(is_active=False)
        self._persist_status()
        LOGGER.info("Kill-switch reset.")

    def check_drawdown(self, max_drawdown_pct: float = 0.10):
        """Trigger if current drawdown from peak equity exceeds limit."""
        equity = self.state_store.account.wallet_balance
        unrealized = self.state_store.account.total_unrealized_pnl
        current_total_equity = equity + unrealized
        
        # Update high-water mark
        if current_total_equity > self.status.peak_equity:
            self.status.peak_equity = current_total_equity
            self._persist_status()

        peak = max(self.status.peak_equity, 1e-9)
        drawdown = (peak - current_total_equity) / peak
        
        if drawdown > max_drawdown_pct:
            self.trigger(
                KillSwitchReason.EXCESSIVE_DRAWDOWN,
                f"Drawdown {drawdown:.2%} exceeded limit {max_drawdown_pct:.2%} (Peak: {peak:.2f}, Current: {current_total_equity:.2f})",
            )

    def check_microstructure(
        self,
        *,
        spread_bps: float | None,
        depth_usd: float | None,
        tob_coverage: float | None,
        max_spread_bps: float,
        min_depth_usd: float,
        min_tob_coverage: float,
    ) -> Dict[str, object]:
        """
        Trigger a live kill-switch when market microstructure exits the tradable envelope.
        """
        gate = evaluate_pretrade_microstructure_gate(
            spread_bps=spread_bps,
            depth_usd=depth_usd,
            tob_coverage=tob_coverage,
            max_spread_bps=max_spread_bps,
            min_depth_usd=min_depth_usd,
            min_tob_coverage=min_tob_coverage,
        )
        if self.status.is_active and self.status.reason not in {
            None,
            KillSwitchReason.MICROSTRUCTURE_BREAKDOWN,
        }:
            gate["is_tradable"] = False
            gate["reasons"] = list(gate.get("reasons", [])) + ["kill_switch_active"]
            gate["recovery_streak"] = int(self.status.recovery_streak)
            gate["required_recovery_streak"] = int(self.microstructure_recovery_streak)
            return gate

        if not gate["is_tradable"]:
            self.status.recovery_streak = 0
            self._persist_status()
            details = ",".join(gate["reasons"]) or "microstructure_breakdown"
            self.trigger(
                KillSwitchReason.MICROSTRUCTURE_BREAKDOWN,
                (
                    f"Pre-trade microstructure gate failed ({details}): "
                    f"spread_bps={gate['spread_bps']}, depth_usd={gate['depth_usd']}, "
                    f"tob_coverage={gate['tob_coverage']}"
                ),
            )
            gate["recovery_streak"] = 0
            gate["required_recovery_streak"] = int(self.microstructure_recovery_streak)
            return gate

        if (
            self.status.is_active
            and self.status.reason == KillSwitchReason.MICROSTRUCTURE_BREAKDOWN
        ):
            self.status.recovery_streak += 1
            if self.status.recovery_streak < self.microstructure_recovery_streak:
                gate["is_tradable"] = False
                gate["reasons"] = ["microstructure_cooldown"]
                gate["recovery_streak"] = int(self.status.recovery_streak)
                gate["required_recovery_streak"] = int(self.microstructure_recovery_streak)
                self.status.message = (
                    "Microstructure recovery in progress "
                    f"({self.status.recovery_streak}/{self.microstructure_recovery_streak})"
                )
                self._persist_status()
                return gate
            self.reset()
            gate["recovered"] = True

        gate["recovery_streak"] = int(self.status.recovery_streak)
        gate["required_recovery_streak"] = int(self.microstructure_recovery_streak)
        return gate


class UnwindOrchestrator:
    """
    Handles the actual closing of positions once a kill-switch is triggered.
    """

    def __init__(self, state_store: LiveStateStore, oms_manager: Any):
        self.state_store = state_store
        self.oms_manager = oms_manager
        self.is_unwinding = False

    async def unwind_all(self):
        """
        Produce market-sell/market-buy orders for all active positions.
        
        Sequentially unwinds positions to avoid overwhelming liquidity.
        """
        if self.is_unwinding:
            return

        self.is_unwinding = True
        try:
            # 1. Cancel all open orders first
            await self.oms_manager.cancel_all_orders()
            
            # 2. Get positions
            positions = self.state_store.account.positions
            if not positions:
                LOGGER.info("No positions to unwind.")
                return

            # Sort by size (USD notional) descending to reduce risk fastest
            sorted_positions = sorted(
                positions.values(), 
                key=lambda p: abs(p.quantity * p.mark_price), 
                reverse=True
            )

            # 3. Flatten positions sequentially with retry logic
            for pos in sorted_positions:
                if abs(pos.quantity) <= 1e-10:
                    continue
                    
                symbol = pos.symbol
                qty = pos.quantity
                side = "SELL" if pos.side == "LONG" else "BUY"
                
                LOGGER.info(f"Unwinding {symbol} {side} {qty}")
                
                # Retry loop for this position
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        # Re-fetch position to get remaining qty
                        current_pos = self.state_store.account.positions.get(symbol)
                        if not current_pos or abs(current_pos.quantity) <= 1e-10:
                            break
                            
                        # Use market order
                        # Note: In a real implementation, we might want to split large orders
                        # For now, we assume the exchange handles the market order splitting or we accept slippage
                        await self.oms_manager.exchange_client.create_market_order(
                            symbol=symbol, 
                            side=side, 
                            quantity=current_pos.quantity, 
                            reduce_only=True
                        )
                        
                        # Wait briefly for fill
                        await asyncio.sleep(1.0)
                        
                        # Check if filled
                        current_pos = self.state_store.account.positions.get(symbol)
                        if not current_pos or abs(current_pos.quantity) <= 1e-10:
                            LOGGER.info(f"Successfully unwound {symbol}")
                            break
                        
                        LOGGER.warning(f"Partial unwind for {symbol}, retrying...")
                        
                    except Exception as e:
                        LOGGER.error(f"Unwind attempt {attempt+1} failed for {symbol}: {e}")
                        await asyncio.sleep(2.0 * (attempt + 1)) # Backoff

            LOGGER.warning("Emergency unwind orchestration completed.")
        except Exception as e:
            LOGGER.error(f"Error during emergency unwind: {e}")
        finally:
            self.is_unwinding = False
