from typing import TypeVar

from faker import Faker
from sqlalchemy import Table

fake = Faker()

T = TypeVar("T")


def to_model(orm_instanse: Table, data_class: type[T]) -> T:
    model = orm_instanse.__dict__
    orm_fields = model.copy()
    fields = data_class.__match_args__

    for field in model:
        if field not in fields:
            orm_fields.pop(field)

    return data_class(**orm_fields)


def update_fields(dict_from_dto: dict, data_from_db: Table):
    for field in dict_from_dto:
        new_value = dict_from_dto[field]
        if new_value is not None and hasattr(data_from_db, field):
            setattr(data_from_db, field, new_value)
    return data_from_db
