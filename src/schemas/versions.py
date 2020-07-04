"""PlanVersion schemas to assist with plans serialization"""
from marshmallow import fields
from src.schemas.schema import ma
from src.schemas.service_codes import PlanSchema
from src.models.versions import PlanVersion


class PlanVersionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = PlanVersion
        include_fk = True
        include_relationships = True
        load_instance = True

    start_effective_date = ma.auto_field()
    end_effective_date = ma.auto_field()
    created_date = ma.auto_field()
    plan = fields.Nested(PlanSchema)