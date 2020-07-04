"""Subscription schema unit test module"""
import pytest
from datetime import datetime
from src.schemas.subscriptions import SubscriptionSchema
from src.schemas.service_codes import PlanSchema


@pytest.fixture(scope="function")
def subscription_with_plan(mocker, db_session, plan_version):
    """Fixture that creates Subscription instance with Plan in DB."""
    sub = plan_version.subscription
    plan = sub.versions[0].plan
    db_session.add(sub)
    db_session.commit()
    sub.select_effective_plan = mocker.MagicMock(return_value=plan)
    return sub


@pytest.fixture(scope="function")
def subscription_schema():
    return SubscriptionSchema()


def convert_to_dictionary(sub, method="GET"):
    """Fixture with JSON expected values."""
    if method == "POST":
        return {
            "id": sub.id,
            "phone_number": sub.phone_number,
            "status": sub.status.value,
        }
    elif method == "GET":
        schema = PlanSchema()
        plan = schema.dump(sub.select_effective_plan(datetime.now()))
        return {
            "id": sub.id,
            "phone_number": sub.phone_number,
            "status": sub.status.value,
            "plan": plan,
            "service_codes": sub.service_codes
        }


def test_schema_pre_load(db_session, subscription_with_plan, subscription_schema):
    """Unit test for loading from DB Subscription instance."""
    requested_load = convert_to_dictionary(subscription_with_plan, "POST")
    sub = subscription_schema.load(requested_load, session=db_session)
    assert sub.id == subscription_with_plan.id
    assert sub.status == subscription_with_plan.status
    assert sub.phone_number == subscription_with_plan.phone_number


def test_schema_post_dump(db_session, subscription_with_plan, subscription_schema):
    """Unit test for getting JSON-formatted response from Subscription."""
    requested_dump = convert_to_dictionary(subscription_with_plan, "GET")
    dump = subscription_schema.dump(subscription_with_plan)
    assert dump == requested_dump
