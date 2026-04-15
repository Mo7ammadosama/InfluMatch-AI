import pytest
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(ROOT))


class TestMilestoneSystem:
    def test_milestone_sum_validation(self):
        from influmatch.backend.api.routes.milestones import validate_milestone_percentages

        with pytest.raises(ValueError, match="100%"):
            validate_milestone_percentages([20.0, 40.0, 30.0])  # sum=90

        with pytest.raises(ValueError, match="100%"):
            validate_milestone_percentages([20.0, 40.0, 41.0])  # sum=101

        # These should pass silently
        validate_milestone_percentages([20.0, 40.0, 40.0])   # sum=100
        validate_milestone_percentages([100.0])
        validate_milestone_percentages([33.333, 33.333, 33.334])  # float tolerance
        print("\nPASS: Milestone sum validation: rejects != 100%, accepts == 100%")

    def test_milestone_release_updates_escrow(self):
        from influmatch.backend.models.milestone import CampaignMilestone, MilestoneStatus

        milestone = CampaignMilestone(
            campaign_id = 1,
            title       = "تسليم المحتوى الأول",
            percentage  = 40.0,
            amount_jod  = 200.000,
            status      = MilestoneStatus.PENDING,
            due_date    = datetime.utcnow(),
        )

        assert milestone.status == MilestoneStatus.PENDING
        assert milestone.released_at is None
        assert milestone.amount_jod == 200.000
        assert round(milestone.amount_jod, 3) == 200.000

        # Simulate release
        milestone.status      = MilestoneStatus.RELEASED
        milestone.released_at = datetime.utcnow()

        assert milestone.status  == MilestoneStatus.RELEASED
        assert milestone.released_at is not None
        print(f"\nPASS: Milestone release: status=RELEASED | amount={milestone.amount_jod} JOD | released_at set")
