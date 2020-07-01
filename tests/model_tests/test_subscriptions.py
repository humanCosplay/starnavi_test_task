import pytest
from datetime import date, timedelta
from src.models.subscriptions import SubscriptionStatus


def test_activate_subscription(db_session, subscription):
    sub = subscription
    assert sub.status == SubscriptionStatus.new

    active_date, is_activated = sub.activate_subscription()
    assert is_activated
    assert active_date.date() == date.today()
    assert sub.expiry_date.date() == date.today() + timedelta(days=30)


@pytest.mark.parametrize("subscription__status", [SubscriptionStatus.active])
def test_activate_subscription_again(db_session, subscription):
    sub = subscription
    assert sub.status == SubscriptionStatus.active

    active_date, is_activated = sub.activate_subscription()
    assert not is_activated


@pytest.mark.parametrize("subscription__status", [SubscriptionStatus.active])
def test_activate_subscription_suspend(db_session, subscription):
    sub = subscription
    assert sub.status == SubscriptionStatus.active

    old_date = sub.expiry_date
    expiry_date, is_suspended = sub.suspend_subscription()
    assert is_suspended
    assert old_date == expiry_date
