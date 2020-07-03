""" Subscription Plan Versions database models and functionality"""
from src.models.base import db
from src.models.cycles import BillingCycle


class PlanVersion(db.Model):
    """It's a ORM class that, represents Subscription-Plan relation.

    For DB attributes see ERD.png file in the project's root
    Help attributes:
        subscription (Subscription): related subscription
        plan (Plan): related Plan

    """
    __tablename__ = "subscription_plan_versions"

    id = db.Column(db.Integer, primary_key=True)
    start_effective_date = db.Column(db.TIMESTAMP(timezone=True))
    end_effective_date = db.Column(db.TIMESTAMP(timezone=True))
    created_date = db.Column(db.TIMESTAMP(timezone=True), index=True)
    subscription_id = db.Column(db.ForeignKey("subscriptions.id"),
                                nullable=False)
    plan_id = db.Column(db.ForeignKey("plans.id"), nullable=False)

    subscription = db.relationship("Subscription", back_populates="versions")
    plan = db.relationship("Plan")

    def __init__(self, **kwargs):
        super(PlanVersion, self).__init__(**kwargs)
        if 'end_effective_date' not in kwargs or \
           'start_effective_date' not in kwargs:
            cycle = BillingCycle.get_current_cycle()
            self._set_end_date(cycle)
            self._set_start_date(cycle)

    def _set_end_date(self, cycle):
        if self.subscription.expiry_date < cycle.end_date:
            self.end_effective_date = self.subscription.expiry_date
        else:
            self.end_effective_date = cycle.end_date

    def _set_start_date(self, cycle):
        if self.subscription.activation_date > cycle.start_date:
            self.start_effective_date = self.subscription.activation_date
        else:
            self.start_effective_date = cycle.start_date
