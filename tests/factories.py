"""
Module for unit testing factory definitions.
Factories generates ORM instances that defined in src.models.*
"""
import factory
from datetime import datetime, timedelta
from src.models.cycles import BillingCycle
from src.models.versions import PlanVersion
from src.models.service_codes import Plan
from src.models.subscriptions import Subscription, SubscriptionStatus


class PlanVersionFactory(factory.Factory):
    """
    PlanVersion ORM factory for testing puprose.

    Depends on Subscription and Plan factories.
    """
    class Meta:
        model = PlanVersion

    start_effective_date = factory.Faker('past_date', start_date='-60d')
    end_effective_date = factory.Faker('future_date', end_date='+60d')
    created_date = factory.LazyFunction(datetime.now)
    plan = factory.SubFactory("tests.factories.PlanFactory")
    subscription = factory.SubFactory("tests.factories.SubscriptionFactory",
                                       versions=None)


class SubscriptionFactory(factory.Factory):
    """
    Subscription ORM factory for testing puprose.

    Has reverse dependency on PlanVersion factory,
    that resolves after Subscription insctance creation
    """
    class Meta:
        model = Subscription

    phone_number = factory.Faker('msisdn')
    status = SubscriptionStatus.new
    activation_date = factory.Faker('past_date', start_date='-60d')
    expiry_date = factory.Faker('future_date', end_date='+60d')

    versions = factory.RelatedFactoryList(
        PlanVersionFactory,
        factory_related_name="subscription",
        size=1
    )


class PlanFactory(factory.Factory):
    """
    Plan ORM factory for testing puprose.
    """
    class Meta:
        model = Plan

    id = factory.Sequence(lambda n: f"Plan #{n}")
    description = factory.Faker('sentence')
    mb_available = factory.Faker('pyint')
    is_unlimited = factory.Faker('pybool')


class BillingCycleFactory(factory.Factory):
    """
    BillingCycle generator for testing puprose.

    Each cycle instance will be 30 days period representation.
    """
    class Meta:
        model = BillingCycle

    start_date = factory.Sequence(lambda month: datetime.now() + timedelta(days=30*month))
    end_date = factory.Sequence(lambda month: datetime.now() + timedelta(days=30*(month + 1)))
