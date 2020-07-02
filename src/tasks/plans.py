"""Plan related tasks"""
from datetime import timedelta
from celery.utils.log import get_task_logger
from src.celery_app import celery
from sqlalchemy import desc, asc
from src.models.base import db
from src.models.versions import PlanVersion
from src.models.service_codes import Plan
from src.models.cycles import BillingCycle

log = get_task_logger(__name__)


@celery.task()
def query_subscription_plans(billing_cycle_id, subscription_id=None):
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    cycle = BillingCycle.query.get(billing_cycle_id)
    result_set = db.session.query(Plan.mb_available,
                                  PlanVersion.start_effective_date,
                                  PlanVersion.end_effective_date).\
                            join(PlanVersion.plan). \
                            filter(PlanVersion.subscription_id == subscription_id,
                                   PlanVersion.start_effective_date >= cycle.start_date,
                                   PlanVersion.end_effective_date <= cycle.end_date).\
                            order_by(asc(Plan.mb_available),
                                     asc(PlanVersion.start_effective_date),
                                     desc(PlanVersion.end_effective_date)).\
                            all()

    def local_min_plan(date):
        for result_row in result_set:
            if date >= result_row[1] and date <= result_row[2]:
                return result_row
        else:
            return None

    result = []
    for day in range((cycle.end_date - cycle.start_date).days):
        local_min = local_min_plan(cycle.end_date - timedelta(days=day))
        if local_min and local_min not in result:
            result.append(local_min)

    return result
