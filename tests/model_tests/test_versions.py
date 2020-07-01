"""SubscriptionPlanVersions model test cases"""
import pytest
from src.models.versions import PlanVersion


def test_dump_version_from_db(db_session, plan_version_factory):
    plan_versions = plan_version_factory.create_batch(5)
    db_session.add_all(plan_versions)
    db_session.commit()

    copy_plan_versions = PlanVersion.query.all()
    for old, new in zip(plan_versions, copy_plan_versions):
        assert old == new
