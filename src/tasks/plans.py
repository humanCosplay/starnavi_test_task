"""Plan related tasks"""
from datetime import timedelta
from celery.utils.log import get_task_logger
from src.celery_app import celery
from sqlalchemy import desc, asc
from src.models.base import db
from src.models.versions import PlanVersion
from src.models.subscriptions import Subscription, SubscriptionStatus
from src.models.service_codes import Plan
from src.models.cycles import BillingCycle

log = get_task_logger(__name__)


def set_proper_start_date(result, new_local_min_end_date):
    """
    Updates an actual effective date of current plan after detecting a new one
    """
    prev_plan, prev_start_date, prev_end_date = result[-1]
    if prev_start_date < new_local_min_end_date:
        prev_start_date = new_local_min_end_date + timedelta(days=1)
        result[-1] = (prev_plan, prev_start_date, prev_end_date)


def lookup_min_plan(date, result_set):
    """
    Returns a minimum plan.
    Result set should be sorted by MB for more efficienty.
    """
    for result_row in result_set:
        if date >= result_row[1] and date <= result_row[2]:
            return result_row
    else:
        return None


def lookup_all_local_min_in_timeline(cycle, result_set):
    """
    Traverses timeline by day from cycle's end to cycle's start and
    looks up in a sorted result_set minimum plan.
    """
    result = []
    for day in range((cycle.end_date - cycle.start_date).days):
        date = cycle.end_date - timedelta(days=day)
        local_min = lookup_min_plan(date, result_set)

        if local_min and local_min not in result:
            if result:
                set_proper_start_date(result, local_min[2])
            result.append(local_min)
    return result


def fetch_sorted_plan_version_by_subscribtion(cycle, sub_id):
    """
    Fetches sorted sub's tariff amount by value and date range.
    """
    return db.session.query(Plan.mb_available,
                            PlanVersion.start_effective_date,
                            PlanVersion.end_effective_date).\
                    join(PlanVersion.plan). \
                    filter(PlanVersion.subscription_id == sub_id,
                           PlanVersion.start_effective_date >= cycle.start_date,
                           PlanVersion.end_effective_date <= cycle.end_date).\
                    order_by(asc(Plan.mb_available),
                             asc(PlanVersion.start_effective_date),
                             desc(PlanVersion.end_effective_date)).\
                    all()


def fetch_sorted_plan_version(cycle):
    """
    Fetches all active plans in given cycle.
    """
    return db.session.query(Plan.mb_available,
                            Subscription.id).\
                    join(PlanVersion.plan).\
                    join(PlanVersion.subscription).\
                    filter(Subscription.status == SubscriptionStatus.active,
                           Subscription.activation_date <= cycle.end_date,
                           Subscription.expiry_date >= cycle.start_date).\
                    all()


def collect_plans_usage(cycle, result_set):
    """
    Merge result_set of active subscription tariffs into dictionary.
    """
    result = {}
    for mb_available, sub_id in result_set:
        if mb_available in result:
            result[mb_available].append(sub_id)
        else:
            result[mb_available] = [sub_id]
    return result


@celery.task()
def query_subscription_plans(billing_cycle_id, subscription_id=None):
    """Add google style doc string here

    (https://www.sphinx-doc.org/en/1.7/ext/example_google.html)

    """
    cycle = BillingCycle.query.get(billing_cycle_id)
    if subscription_id:
        result_set = fetch_sorted_plan_version_by_subscribtion(cycle, subscription_id)
        return lookup_all_local_min_in_timeline(cycle, result_set)
    else:
        result_set = fetch_sorted_plan_version(cycle)
        return collect_plans_usage(cycle, result_set)
