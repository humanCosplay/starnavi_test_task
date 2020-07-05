from datetime import datetime, timezone, timedelta
from src.models.base import db
from src.models.cycles import BillingCycle
from src.models.service_codes import Plan, ServiceCode
from src.models.subscriptions import Subscription
from src.models.usages import DataUsage
from src.models.versions import PlanVersion
from tests import factories


def db_init():
    """ Function that initialize database for development."""
    db.drop_all()
    db.create_all()
    
    factories.BillingCycleFactory.reset_sequence(0)        
    cycles = factories.BillingCycleFactory.create_batch(3)
    db.session.add_all(cycles)
    db.session.commit()

    plan_args = [
        {
            'id': "Plan #1",
            'description': '1GB Monthly Data Plan',
            'mb_available': '1024',
            'is_unlimited': False
        },
        {
            'id': "Plan #2",
            'description': '5GB Monthly Data Plan',
            'mb_available': '5120',
            'is_unlimited': False
        },
        {
            'id': "Plan #3",
            'description': 'Unlimited Monthly Data Plan',
            'mb_available': '10240',
            'is_unlimited': True
        }
    ]
    plans = [Plan(**pa_args) for pa_args in plan_args]
    db.session.add_all(plans)
    db.session.commit()
    
    service_codes_args = [
        {
            'name': 'Data Block',
            'description': 'Blocks all data',
        },
        {
            'name': 'International Calling',
            'description': 'Enables international calling',
        }
    ]
    service_codes = [ServiceCode(**sc_args) for sc_args in service_codes_args]
    db.session.add_all(service_codes)
    db.session.commit()
    
    subs = [
        {
            'phone_number': '1111111111',
            'status': 'active',
            'activation_date': cycles[1].start_date,
            'expiry_date': cycles[1].end_date
        },
        {
            'phone_number': '2222222222',
            'status': 'suspended',
            'service_codes': [service_codes[0]]
        },
        {
            'phone_number': '3333333333',
            'status': 'new',
        },
        {
            'phone_number': '4444444444',
            'status': 'expired',
        },
        {
            'phone_number': '5555555555',
            'status': 'active',
            'activation_date': cycles[0].start_date,
            'expiry_date': cycles[1].end_date - timedelta(days=10)
        },
        {
            'phone_number': '7777777777',
            'status': 'suspended',
        },
        {
            'phone_number': '8888888888',
            'status': 'active',
            'activation_date': cycles[1].start_date + timedelta(days=10),
            'expiry_date': cycles[2].end_date
        }
    ]
    subs = [Subscription(**s_args) for s_args in subs]
    db.session.add_all(subs)
    db.session.commit()


    plan_version_args = [
        {
            'subscription': subs[0],
            'plan': plans[1]
        },
        {
            'subscription': subs[0],
            'plan': plans[0]
        },
        {
            'subscription': subs[2],
            'plan': plans[0]
        },
        {
            'subscription': subs[4],
            'plan': plans[2]
        },
        {
            'subscription': subs[4],
            'plan': plans[0]
        },
        {
            'subscription': subs[6],
            'plan': plans[1]
        },
        {
            'subscription': subs[6],
            'plan': plans[2]
        }
    ]

    plan_versions = [PlanVersion(**pv_args) for pv_args in plan_version_args]
    db.session.add_all(plan_versions)
    db.session.commit()


    data_usage_args = [
        {
            'id': 1,
            'mb_used': 121.522,
            'from_date': datetime(2020, 8, 20, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 1
        },
        {
            'id': 2,
            'mb_used': 519.984,
            'from_date': datetime(2020, 8, 21, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 21, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 1
        },
        {
            'id': 3,
            'mb_used': 22.362,
            'from_date': datetime(2020, 8, 24, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 24, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 1
        },
        {
            'id': 4,
            'mb_used': 450.759,
            'from_date': datetime(2020, 8, 3, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 3, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 2
        },
        {
            'id': 5,
            'mb_used': 560.811,
            'from_date': datetime(2020, 8, 10, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 10, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 4
        },
        {
            'id': 6,
            'mb_used': 220.336,
            'from_date': datetime(2020, 8, 20, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 5
        },
        {
            'id': 7,
            'mb_used': 51.553,
            'from_date': datetime(2020, 8, 20, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 5
        },
        {
            'id': 8,
            'mb_used': 470.288,
            'from_date': datetime(2020, 8, 9, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 9, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 6
        },
        {
            'id': 9,
            'mb_used': 221.02,
            'from_date': datetime(2020, 8, 20, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 20, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 7
        },
        {
            'id': 10,
            'mb_used': 1896.663,
            'from_date': datetime(2020, 8, 12, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 12, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 7
        },
        {
            'id': 11,
            'mb_used': 2216.993,
            'from_date': datetime(2020, 8, 13, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 13, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 7
        },
        {
            'id': 12,
            'mb_used': 1151.444,
            'from_date': datetime(2020, 8, 14, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 14, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 7
        },
        {
            'id': 13,
            'mb_used': 829.334,
            'from_date': datetime(2020, 8, 19, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 19, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 2
        },
        {
            'id': 14,
            'mb_used': 10299.012,
            'from_date': datetime(2020, 8, 2, tzinfo=timezone.utc),
            'to_date': datetime(2020, 8, 2, 23, 59, 59, 999999, tzinfo=timezone.utc),
            'subscription_id': 1
        }
    ]
    data_usage = [DataUsage(**da_args) for da_args in data_usage_args]
    db.session.add_all(data_usage)
    db.session.commit()