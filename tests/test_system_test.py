"""Smoke test module of test system.

Checks its basic behavior and could serve as an example for future test modules.
"""
import pytest
from src.models.cycles import BillingCycle


@pytest.fixture(scope="function")
def db_cycles(db_session, billing_cycle_factory):
    """ Fixture for setting up test db and factory. """

    billing_cycle_factory.reset_sequence(0)
    db_cycles = billing_cycle_factory.create_batch(5)
    db_session.add_all(db_cycles)
    db_session.commit()
    return db_cycles


def test_get_cycle(db_session, db_cycles):
    """ First test of test system's transactional behavior via db_session.

    db_session is a mocked SQLAlchemy fixture from pytest-flask-sqlalchemy.
    """
    cycle = db_session.query(BillingCycle).first()
    assert cycle.start_date == db_cycles[0].start_date


def test_get_cycle_again(db_session, billing_cycle_factory):
    """ Second test of transactional behavior.

    Check your pytest-flask-sqlalchemy configuration if test fails.
    """
    cycle = db_session.query(BillingCycle).all()
    assert len(cycle) == 0
