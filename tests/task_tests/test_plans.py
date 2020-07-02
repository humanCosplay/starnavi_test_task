import pytest
from datetime import timedelta
from src.models.versions import PlanVersion
from src.tasks.plans import query_subscription_plans


@pytest.fixture(scope="function")
def plans(db_session,  plan_factory):
    plans = plan_factory.create_batch(5)
    db_session.add_all(plans)
    db_session.commit()
    return sorted(plans, key=lambda p: p.mb_available)


@pytest.fixture(scope="function")
def cycles(db_session, billing_cycle_factory):
    billing_cycle_factory.reset_sequence(0)
    cycles = billing_cycle_factory.create_batch(5)
    db_session.add_all(cycles)
    db_session.commit()
    return cycles


def compare_query_result_tuple(result, expected_version):
    return result[0] == expected_version.plan.mb_available \
       and result[1] == expected_version.start_effective_date \
       and result[2] == expected_version.end_effective_date


def version_pair(db_session, cycle, sub, plan_set, shifts):
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
def test_get_subscribtion_plan(db_session, plans, cycles, subscription):
    sub = subscription

    version = PlanVersion(subscription=sub, plan=plans[0])
    db_session.add(version)
    db_session.commit()

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    assert compare_query_result_tuple(query_result[0], version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_overlapped_old(db_session, plans, cycles, subscription):
    sub = subscription
    optimal, _ = version_pair(db_session, cycles[0], sub, plans, (18, 0))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    assert len(query_result) == 1
    assert compare_query_result_tuple(query_result[0], optimal)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_overlapped_optimal(db_session, plans, cycles, subscription):
    sub = subscription
    expected = version_pair(db_session, cycles[0], sub, plans, (30, 15))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    assert len(query_result) == 2
    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_intersects(db_session, plans, cycles, subscription):
    sub = subscription

    expected = version_pair(db_session, cycles[0], sub, plans, (18, 10))
    query_result = query_subscription_plans(cycles[0].id, sub.id)

    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_gapped(db_session, plans, cycles, subscription):
    sub = subscription
    expected = version_pair(db_session, cycles[0], sub, plans, (10, 20))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)


@pytest.mark.parametrize("subscription__versions", [[]])
def test_subscribtion_plan_joined(db_session, plans, cycles, subscription):
    sub = subscription
    expected = version_pair(db_session, cycles[0], sub, plans, (15, 15))

    query_result = query_subscription_plans(cycles[0].id, sub.id)

    for res, version in zip(query_result, expected):
        assert compare_query_result_tuple(res, version)
