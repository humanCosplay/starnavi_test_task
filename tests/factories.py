"""
Module for factory definitions for unit testing.
Factories generates ORM instances that defined in src.models.*
"""
import factory
from datetime import datetime, timedelta
from src.models.cycles import BillingCycle


class BillingCycleFactory(factory.Factory):
    """
    BillingCycle generator for testing puprose.
    Each cycle instance will be 30 days period representation.
    """
    class Meta:
        model = BillingCycle

    start_date = factory.Sequence(lambda month: datetime.now() + timedelta(days=30*month))
    end_date = factory.Sequence(lambda month: datetime.now() + timedelta(days=30*(month + 1)))
