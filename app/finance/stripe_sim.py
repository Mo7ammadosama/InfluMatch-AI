"""
WaslAI.jo — Stripe Payment Simulation
Test mode — JOD currency simulation (Stripe uses minor units)
1 JOD = 100 fils (treated as cents in Stripe API)
"""
import stripe
from loguru import logger
from app.config import settings

stripe.api_key = settings.stripe_secret_key

JOD_TO_FILS = 100


def jod_to_fils(amount_jod: float) -> int:
    return int(round(amount_jod * JOD_TO_FILS))


async def create_payment_intent(amount_jod: float, metadata: dict | None = None) -> dict:
    try:
        intent = stripe.PaymentIntent.create(
            amount=jod_to_fils(amount_jod),
            currency="jod",
            payment_method_types=["card"],
            metadata=metadata or {},
            description=f"WaslAI.jo Escrow | {amount_jod} JOD",
        )
        logger.info(f"Stripe PaymentIntent created: {intent.id} | {amount_jod} JOD")
        return {"payment_intent_id": intent.id, "client_secret": intent.client_secret, "status": intent.status}
    except stripe.error.StripeError as e:
        logger.warning(f"Stripe error (using sim mode): {e}")
        return {
            "payment_intent_id": f"pi_sim_{id(amount_jod)}",
            "client_secret": "sim_secret",
            "status": "requires_payment_method",
            "simulated": True,
        }


async def simulate_payment_success(payment_intent_id: str) -> dict:
    logger.info(f"[SIM] Payment success for {payment_intent_id}")
    return {"payment_intent_id": payment_intent_id, "status": "succeeded", "simulated": True}
