""" Unit test module of BillingCycle model """
import pytest
from datetime import datetime, timedelta
from src.models.cycles import BillingCycle


@pytest.fixture(scope="function")
def db_cycles(db_session, billing_cycle_factory):
    """ Pytest fixture for setting up test.

    Resets factory and fill db with test date.

    Returns:
        List of BillingCycle instances.

    """
    billing_cycle_factory.reset_sequence(0)
    db_cycles = billing_cycle_factory.create_batch(5)
    db_session.add_all(db_cycles)
    db_session.commit()
    return db_cycles


def test_get_current_cycle(db_session, db_cycles):
    """ Test checks getting default cycle from DB (default=current). """

    current_cycle = BillingCycle.get_current_cycle()
    assert db_cycles[0] == current_cycle


def test_get_cycle_after_80_days(db_session, db_cycles):
    """Test checks getting specific cycle from DB.

    Factory generates cycles as 30 days range,
        so 'future_cycle' should be third in the list.

    """
    date_after_trip = datetime.now() + timedelta(days=80)
    future_cycle = BillingCycle.get_current_cycle(date_after_trip)
    assert db_cycles[2] == future_cycle
