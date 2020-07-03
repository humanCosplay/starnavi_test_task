"""Unit test module for src.tasks.plan."""
import pytest
from datetime import timedelta
from src.models.versions import PlanVersion
from src.models.subscriptions import SubscriptionStatus
from src.tasks.plans import query_subscription_plans


@pytest.fixture(scope="function")
def plans(db_session,  plan_factory):
    """ Pytest fixture for setting up test.

    Reset PlanFactory and fill db with test Plan instances.

    Returns:
        List of Plan instances.

    """
    plans = plan_factory.create_batch(5)
    db_session.add_all(plans)
    db_session.commit()
    return sorted(plans, key=lambda p: p.mb_available)


@pytest.fixture(scope="function")
def cycles(db_session, billing_cycle_factory):
    """ Pytest fixture for setting up test.

    Resets factory and fill db with test date.

    Returns:
        List of BillingCycle instances.

    """
    billing_cycle_factory.reset_sequence(0)
    cycles = billing_cycle_factory.create_batch(5)
    db_session.add_all(cycles)
    db_session.commit()
    return cycles


def compare_query_result_tuple(result, expected_version):
    return result[0] == expected_version.plan.mb_available \
           and result[1] >= expected_version.start_effective_date


def version_pair(db_session, cycle, sub, plan_set, shifts):
    """ Set up test function.

    Creates PlanVersion instances, store them in db.

    Arguments:
        db_session: pytest fixture from pytest_flask_sqlalchemy.
        cycle: BillingCycle instance.
        sub: Subscription instance.
        plan_set: 2 Plan instance.
        shifts: day shifts for each PlanVersion.

    Returns:
        Tuple with 2 PlanVersion instances.

    """
    s_date = cycle.start_date
    e_date = cycle.start_date + timedelta(days=shifts[0])
    old = PlanVersion(subscription=sub,
                      plan=plan_set[1],
                      start_effective_date=s_date,
                      end_effective_date=e_date)

    s_date = cycle.start_date + timedelta(days=shifts[1])
    e_date = cycle.end_date
    opt = PlanVersion(subscription=sub,
                      plan=plan_set[0],
                      start_effective_date=s_date,
                      end_effective_date=e_date)

    db_session.add(old)
    db_session.add(opt)
    db_session.commit()
    return (opt, old)


@pytest.mark.parametrize("subscription__versions", [[]])
@pytest.mark.parametrize("subscription__status", [SubscriptionStatus.active])
def test_get_subscribtion_plan(db_session, plans, cycles, subscription):
    """Ping-Pong test for query.

    Creates one PlanVersion instance.
    Query returns it.

    """
    sub = subscription

    version = PlanVersion(subscription=sub, plan=plans[0])
    db_session.add(version)
    db_session.commit()

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    assert compare_query_result_tuple(query_result[0], version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_overlapped_old(db_session, plans, cycles, subscription):
    """Test for overlapped old plan with optimal.

    Query should return only optimal plan.
    """
    sub = subscription
    optimal = version_pair(db_session, cycles[0], sub, plans, (18, 0))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    assert len(query_result) == 1
    for res, version in zip(query_result, optimal):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_overlapped_optimal(db_session, plans, cycles, subscription):
    """Test for overlapped optimal plan with old.

    Query should return optimal plan till its end
        and old plan in rest of billing cycle.
    """
    sub = subscription
    expected = version_pair(db_session, cycles[0], sub, plans, (30, 15))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    assert len(query_result) == 2
    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_intersects(db_session, plans, cycles, subscription):
    """Test for intersetion of optimal plan and old.

    Query should return optimal plan till its end
        and old plan in rest of billing cycle.
    """
    sub = subscription

    expected = version_pair(db_session, cycles[0], sub, plans, (18, 10))
    query_result = query_subscription_plans(cycles[0].id, sub.id)

    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_gapped(db_session, plans, cycles, subscription):
    """Test optimal plan and old with gap between them.

    Query should return both of them without changes in dates.

    """
    sub = subscription
    expected = version_pair(db_session, cycles[0], sub, plans, (10, 20))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_joined(db_session, plans, cycles, subscription):
    """Test optimal plan and old chained in 1 day

    Query should return both of them without changes in dates.

    """
    sub = subscription
    expected = version_pair(db_session, cycles[0], sub, plans, (15, 15))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


def test_subscribtion_plan_default(db_session, subscription_factory, plans, cycles):
    """ Test of default query_subscription_plans execution.

    Creates 5 Plan-Subscription pairs, store them in db.
    Query should return them back in dictionary format {mb_available:[subscription_id]}.

    """
    subs = subscription_factory.create_batch(5, versions=[], status=SubscriptionStatus.active)
    pv = [PlanVersion(subscription=sub, plan=plan) for sub, plan in zip(subs, plans)]

    db_session.add_all(subs)
    db_session.add_all(pv)
    db_session.commit()

    query_result = query_subscription_plans(cycles[0].id)
    assert len(query_result) == len(pv)
    for sub, plan in zip(subs, plans):
        assert plan.mb_available in query_result
        assert query_result[plan.mb_available] == [sub.id]


def test_subscribtion_plan_default_for_not_active(db_session, subscription_factory, plans, cycles):
    """ Test of default query_subscription_plans execution.

    Creates 5 Plan-Subscription not active pairs, store them in db.
    Query result shoul be empty.

    """
    subs = subscription_factory.create_batch(5, versions=[], status=SubscriptionStatus.suspended)
    pv = [PlanVersion(subscription=sub, plan=plan) for sub, plan in zip(subs, plans)]

    db_session.add_all(subs)
    db_session.add_all(pv)
    db_session.commit()

    query_result = query_subscription_plans(cycles[0].id)
    assert len(query_result) == 0
