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
    def local_min_plan(date):
        """
        Returns a minimum plan.
        Result set should be sorted by MB for more efficienty.
        """
        for result_row in result_set:
            if date >= result_row[1] and date <= result_row[2]:
                return result_row
        else:
            return None

    def set_proper_start_date(result, new_local_min_end_date):
        """
        Updates an actual effective date of current plan after detecting a new one
        """
        prev_plan, prev_start_date, prev_end_date = result[-1]
        if prev_start_date < new_local_min_end_date:
            prev_start_date = new_local_min_end_date + timedelta(days=1)
            result[-1] = (prev_plan, prev_start_date, prev_end_date)

    def lookup_all_local_min_in_timeline(cycle):
        """
        Traverses timeline by day from cycle's end to cycle's start and
        looks up in sorted result_set minimum plan.
        """
        result = []
        for day in range((cycle.end_date - cycle.start_date).days):
            local_min = local_min_plan(cycle.end_date - timedelta(days=day))
            if local_min and local_min not in result:
                if result:
                    set_proper_start_date(result, local_min[2])
                result.append(local_min)
        return result

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

    return lookup_all_local_min_in_timeline(cycle)
