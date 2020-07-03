"""Subscription unit test module"""
import pytest
from datetime import date, timedelta, datetime
from src.models.subscriptions import SubscriptionStatus
from src.models.versions import PlanVersion
from tests.model_tests.test_cycles import db_cycles


def test_activate_subscription(db_session, subscription):
    """ Test subscription instance activation.

    Instance should change status from default("new") to "active".
    Also it should update activation and expiry date.

    """
    sub = subscription
    assert sub.status == SubscriptionStatus.new

    active_date, is_activated = sub.activate_subscription()
    assert is_activated
    assert active_date.date() == date.today()
    assert sub.expiry_date.date() == date.today() + timedelta(days=30)


@pytest.mark.parametrize("subscription__status", [SubscriptionStatus.active])
def test_activate_subscription_again(db_session, subscription):
    """ Test subscription instance activation.

    Instance should not be changed.

    """
    sub = subscription
    assert sub.status == SubscriptionStatus.active

    active_date, is_activated = sub.activate_subscription()
    assert not is_activated


@pytest.mark.parametrize("subscription__status", [SubscriptionStatus.active])
def test_activate_subscription_suspend(db_session, subscription):
    """ Test subscription instance suspending.

    Instance should change status only.

    """
    sub = subscription
    assert sub.status == SubscriptionStatus.active

    old_date = sub.expiry_date
    expiry_date, is_suspended = sub.suspend_subscription()
    assert is_suspended
    assert old_date == expiry_date


@pytest.mark.parametrize("subscription__versions", [[]])
def test_select_effective_plan_for_subscription(db_cycles, subscription, plan_factory):
    """ Test selecting effective plan dynamicly.

    Instance should return a Plan with a minimal mb_available value.

    """
    sub = subscription
    plans = plan_factory.create_batch(2)
    sub.activate_subscription()
    for plan in plans:
        PlanVersion(subscription=sub, plan=plan)

    expected_plan = min(plans, key=lambda plan: plan.mb_available)
    result = sub.select_effective_plan(datetime.now())
    assert expected_plan == result