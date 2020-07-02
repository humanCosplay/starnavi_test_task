"""Subscription schemas to assist with sub serialization"""
from datetime import datetime
from marshmallow import fields, post_dump
from src.models.subscriptions import Subscription
from src.schemas.schema import ma
from src.schemas.service_codes import PlanSchema


class SubscriptionSchema(ma.SQLAlchemySchema):
    """Schema class to handle serialization of subscription data"""
    class Meta:
        model = Subscription
        include_fk = True

    id = ma.auto_field()
    phone_number = ma.auto_field()
    service_codes = fields.Method("get_service_codes")
    status = fields.Method("get_status_name")

    def get_service_codes(self, obj):
        """field get method to return service code names"""
        return [code.name for code in obj.service_codes]

    def get_status_name(self, obj):
        """field get method to get SupscriptionEnum value"""
        return obj.status.value

    @post_dump(pass_original=True)
    def get_current_plan(self, data, orig, **kwargs):
        """Wrapper method that calls Subscription.select_effective_plan"""
        plan = orig.select_effective_plan(datetime.now())
        schema = PlanSchema()
        data["plan"] = schema.dump(plan)
        return data
