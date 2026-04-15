# Ensures all models are imported so SQLAlchemy creates tables
# ============================================================

from .user        import User, UserRole
from .merchant    import Merchant
from .influencer  import Influencer
from .campaign    import Campaign, CampaignStatus, CampaignInfluencer
from .contract    import Contract, ContractStatus
from .escrow      import EscrowTransaction, EscrowStatus
from .wallet      import LoyaltyWallet, WalletTransaction, TransactionType
from .milestone   import CampaignMilestone, MilestoneStatus
from .campaign_report import CampaignReport, ReportStatus
from .booking import Booking, BookingStatus

__all__ = [
    "User", "UserRole",
    "Merchant",
    "Influencer",
    "Campaign", "CampaignStatus", "CampaignInfluencer",
    "Contract", "ContractStatus",
    "EscrowTransaction", "EscrowStatus",
    "LoyaltyWallet", "WalletTransaction", "TransactionType",
    "CampaignMilestone", "MilestoneStatus",
    "CampaignReport", "ReportStatus",
    "Booking", "BookingStatus",
]
# ============================================================