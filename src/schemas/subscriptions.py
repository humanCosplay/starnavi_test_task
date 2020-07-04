"""Subscription schemas to assist with sub serialization"""
from datetime import datetime
from marshmallow import fields, Schema
from src.schemas.schema import ma
from src.schemas.service_codes import PlanSchema
from src.models.subscriptions import Subscription, SubscriptionStatus


class SubscriptionSchema(ma.SQLAlchemySchema):
    """Schema class to handle serialization of subscription data"""
    class Meta:
        model = Subscription
        include_fk = True
        include_relationships = True
        load_instance = True

    id = ma.auto_field()
    phone_number = ma.auto_field()
    service_codes = fields.Method("get_service_codes")
    status = fields.Method("get_status_name", deserialize="set_status")
    plan = fields.Method("select_plan")

    def get_service_codes(self, obj):
        """field get method to return service code names"""
        return [code.name for code in obj.service_codes]

    def get_status_name(self, obj):
        """field get method to get SupscriptionEnum value"""
        return obj.status.value

    def set_status(self, name):
        """obj.status field deserializer"""
        return SubscriptionStatus(name)

    def select_plan(self, obj):
        """Returns effective plan only"""
        plan = obj.select_effective_plan(datetime.now())
        schema = PlanSchema()
        return schema.dump(plan)


class SubscriptionQuerySchema(Schema):
    id = fields.Integer()
    phone_number = fields.String()
    status = fields.String()