""" Configuration of test system module """
import pytest
import config

from pytest_factoryboy import register
from tests.factories import BillingCycleFactory
from src import create_app
from src.models.base import db

register(BillingCycleFactory)


@pytest.fixture(scope="session")
def app(request):
    """ Create Flask testing app """

    app = create_app(config.TestingConfiguration)
    return app


@pytest.fixture
def client(app):
    """ Create Flask testing app's client."""

    return app.test_client()


@pytest.fixture(scope="session")
def _db(app):
    """ Fixture for transactional testing via pytest-flask-sqlalchemy """

    db.drop_all()
    db.create_all()
    return db
