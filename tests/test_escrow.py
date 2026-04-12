"""
InfluMatch.jo — Escrow State Machine Tests
PENDING → FUNDED → LOCKED → RELEASED
"""
import pytest
from app.services.escrow_service import EscrowService, VALID_TRANSITIONS
from app.models.escrow import EscrowState


def test_valid_transitions_completeness():
    for state in EscrowState:
        assert state in VALID_TRANSITIONS, f"Missing transitions for state: {state}"


def test_escrow_fee_calculation():
    service = EscrowService()
    amounts = service.calculate_amounts(100.0)

    assert amounts["gross_amount_jod"] == 100.0
    assert amounts["platform_fee_jod"] == pytest.approx(5.0, abs=0.01)
    assert amounts["vat_on_fee_jod"] == pytest.approx(0.8, abs=0.01)
    assert amounts["net_to_influencer_jod"] == pytest.approx(94.2, abs=0.01)


def test_escrow_state_machine_paths():
    valid = VALID_TRANSITIONS
    assert EscrowState.FUNDED in valid[EscrowState.PENDING]
    assert EscrowState.LOCKED in valid[EscrowState.FUNDED]
    assert EscrowState.RELEASED in valid[EscrowState.LOCKED]
    assert EscrowState.DISPUTED in valid[EscrowState.LOCKED]
    assert len(valid[EscrowState.RELEASED]) == 0
    assert len(valid[EscrowState.REFUNDED]) == 0


def test_escrow_fee_edge_cases():
    service = EscrowService()
    amounts = service.calculate_amounts(50.0)
    assert amounts["gross_amount_jod"] == 50.0
    assert amounts["net_to_influencer_jod"] > 0

    amounts2 = service.calculate_amounts(1000.0)
    assert amounts2["platform_fee_jod"] == pytest.approx(50.0, abs=0.01)
