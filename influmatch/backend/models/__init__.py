# Ensures all models are imported so SQLAlchemy creates tables
# ============================================================

from .user        import User, UserRole
from .merchant    import Merchant
from .influencer  import Influencer
from .campaign    import Campaign, CampaignStatus, CampaignInfluencer
from .contract    import Contract, ContractStatus
from .escrow      import EscrowTransaction, EscrowStatus
from .wallet      import LoyaltyWallet, WalletTransaction, TransactionType

__all__ = [
    "User", "UserRole",
    "Merchant",
    "Influencer",
    "Campaign", "CampaignStatus", "CampaignInfluencer",
    "Contract", "ContractStatus",
    "EscrowTransaction", "EscrowStatus",
    "LoyaltyWallet", "WalletTransaction", "TransactionType"
]
# ============================================================