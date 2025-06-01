from sqlalchemy.inspection import inspect
from typing import Type

from sqlalchemy.orm import InstrumentedAttribute

from equipment.models import BaseModel

def model_to_dict(obj):
    return {
        c.key: getattr(obj, c.key)
        for c in inspect(obj).mapper.column_attrs
    }

def get_instrumented_attribute_name(domain: Type[BaseModel], instrumentedAttribute: InstrumentedAttribute):
    name_table = str(domain.__name__)
    return str(instrumentedAttribute).replace(f"{name_table}.", "")