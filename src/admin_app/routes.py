from flask_admin.contrib.sqla import ModelView
from src.admin_app import admin
from src.models.base import db
from src.models.subscriptions import Subscription
from src.models.versions import PlanVersion
from src.models.service_codes import Plan, ServiceCode
from src.models.usages import DataUsage
from src.models.cycles import BillingCycle


admin.add_view(ModelView(BillingCycle, db.session))
admin.add_view(ModelView(Plan, db.session))
admin.add_view(ModelView(ServiceCode, db.session))
admin.add_view(ModelView(PlanVersion, db.session))
admin.add_view(ModelView(Subscription, db.session))
admin.add_view(ModelView(DataUsage, db.session))