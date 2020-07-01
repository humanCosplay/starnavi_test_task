"""SubscriptionPlanVersions model test cases"""
import pytest
from datetime import datetime, timedelta
from src.models.versions import PlanVersion
from tests.model_tests.test_cycles import db_cycles


def test_get_version_from_db(db_session, plan_version_factory):
    plan_versions = plan_version_factory.create_batch(5)
    db_session.add_all(plan_versions)
    db_session.commit()

    copy_plan_versions = PlanVersion.query.all()
    for old, new in zip(plan_versions, copy_plan_versions):
        assert old == new


@pytest.mark.parametrize("subscription__activation_date", [datetime.now() - timedelta(days=15)])
@pytest.mark.parametrize("subscription__expiry_date", [datetime.now() + timedelta(days=45)])
def test_create_version_manually(
    db_session, db_cycles,
    plan, subscription):\

    default_version = PlanVersion(plan=plan, subscription=subscription)
    assert default_version.start_effective_date == db_cycles[0].start_date
    assert default_version.end_effective_date == db_cycles[0].end_date


@pytest.mark.parametrize("subscription__activation_date", [datetime.now() + timedelta(days=5)])
@pytest.mark.parametrize("subscription__expiry_date", [datetime.now() + timedelta(days=45)])
def test_create_version_manually_for_activated_sub_in_future(
    db_session, db_cycles,
    plan, subscription):\

    default_version = PlanVersion(plan=plan, subscription=subscription)
    assert default_version.start_effective_date == subscription.activation_date
    assert default_version.end_effective_date == db_cycles[0].end_date



@pytest.mark.parametrize("subscription__activation_date", [datetime.now() - timedelta(days=45)])
@pytest.mark.parametrize("subscription__expiry_date", [datetime.now() + timedelta(days=5)])
def test_create_version_manually_for_expiring_sub_soon(
    db_session, db_cycles,
    plan, subscription):\


    default_version = PlanVersion(plan=plan, subscription=subscription)
    assert default_version.start_effective_date == db_cycles[0].start_date
    assert default_version.end_effective_date == subscription.expiry_date



@pytest.mark.parametrize("subscription__activation_date", [datetime.now() + timedelta(days=5)])
@pytest.mark.parametrize("subscription__expiry_date", [datetime.now() + timedelta(days=15)])
def test_create_version_manually_for_short_sub(
    db_session, db_cycles,
    plan, subscription):\


    default_version = PlanVersion(plan=plan, subscription=subscription)
    assert default_version.start_effective_date == subscription.activation_date
    assert default_version.end_effective_date == subscription.expiry_date


def test_create_version_manually_with_dates(
    db_session, db_cycles,
    plan, subscription):\

    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=30)

    default_version = PlanVersion(plan=plan,
                                  subscription=subscription,
                                  start_effective_date=start_date,
                                  end_effective_date=end_date)
    assert default_version.start_effective_date == start_date
    assert default_version.end_effective_date == end_date
