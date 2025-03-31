from sqlalchemy import Table


def update_fields(dict_from_dto: dict, data_from_db: Table):
    for field in dict_from_dto:
        new_value = dict_from_dto[field]
        if new_value is not None and hasattr(data_from_db, field):
            setattr(data_from_db, field, new_value)
    return data_from_db
