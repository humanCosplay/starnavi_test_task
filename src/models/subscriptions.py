"""Subscription related models and database functionality"""
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy.dialects.postgresql import ENUM
from src.models.base import db
from src.models.service_codes import subscriptions_service_codes
from src.models.usages import DataUsage
from src.models.versions import PlanVersion


class SubscriptionStatus(Enum):
    """Enum representing possible subscription statuses"""
    new = "new"
    active = "active"
    suspended = "suspended"
    expired = "expired"


class Subscription(db.Model):
    """Model class to represent ATT subscriptions"""

    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(10))
    status = db.Column(ENUM(SubscriptionStatus),
                       default=SubscriptionStatus.new)
    activation_date = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    expiry_date = db.Column(db.TIMESTAMP(timezone=True), nullable=True)
    service_codes = db.relationship(
        "ServiceCode", secondary=subscriptions_service_codes,
        primaryjoin="Subscription.id==subscriptions_service_codes.c.subscription_id",
        secondaryjoin="ServiceCode.id==subscriptions_service_codes.c.service_code_id",
        back_populates="subscriptions", cascade="all,delete", lazy="subquery"
    )
    data_usages = db.relationship(DataUsage, back_populates="subscription")
    versions = db.relationship(PlanVersion, back_populates="subscription")

    def __repr__(self):  # pragma: no cover
        return (
            f"<{self.__class__.__name__}: {self.id} ({self.status}), "
            f"phone_number: {self.phone_number or '[no phone number]'}, ",
            f"plan: {self.plan_id}>"
        )

    @classmethod
    def get_subscriptions(cls, **kwargs):
        """Gets a list of Subscription objects using given kwargs

        Generates query filters from kwargs param using base class method

        Args:
            kwargs: key value pairs to apply as filters

        Returns:
            list: objects returned from query result

        """
        return cls.query.filter(**kwargs).all()

    @property
    def service_code_names(self):
        """Helper property to return names of active service codes"""
        return [code.name for code in self.service_codes]

    def activate_subscription(self):
        """Set subscription.status as 'active'

        Returns:
            'datetime': activation_datetime of instance,
            'bool': if method has activated instance.

        """
        if self.status == SubscriptionStatus.active:
            return (self.activation_date, False)

        self.status = SubscriptionStatus.active
        self.activation_date = datetime.now()
        self.expiry_date = self.activation_date + timedelta(days=30)
        db.session.add(self)
        return (self.activation_date, True)

    def suspend_subscription(self):
        """Set subscription.status as 'suspend'

        Returns:
            'datetime': expiry datetime of instance,
            'bool': if method has suspended instance.

        """
        if self.status == SubscriptionStatus.suspended:
            return (self.expiry_date, False)

        self.status = SubscriptionStatus.suspended
        db.session.add(self)
        return (self.expiry_date, True)

    def select_effective_plan(self, date):
        """Selects currently effective plan

        Returns:
            'Plan': the most effective Plan instance by min mb_available
        """
        def lookup_by_date(version, date):
            return version.start_effective_date <= date \
                and version.end_effective_date >= date

        def mb_sorted(versions):
            return sorted(versions, key=lambda v: v.plan.mb_available)

        for v in mb_sorted(self.versions):
            if lookup_by_date(v, date):
                return v.plan
        else:
            return None
