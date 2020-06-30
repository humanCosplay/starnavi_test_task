"""Service code schemas to assist with service code / plan serialization"""
from src.schemas.schema import ma
from src.models.service_codes import Plan, ServiceCode


class PlanSchema(ma.SQLAlchemySchema):
    """Schema class to handle serialization of plan data"""
    class Meta:
        model = Plan
        include_fk = True
 
    id = ma.auto_field()
    description = ma.auto_field()


class ServiceCodeSchema(ma.SQLAlchemySchema):
    """Schema class to handle serialization of simplified service code data"""
    class Meta:
        model = ServiceCode
        include_fk = True
    
    name = ma.auto_field()
    description = ma.auto_field()
