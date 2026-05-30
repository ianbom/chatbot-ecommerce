from enum import Enum

from sqlalchemy import Enum as SAEnum


def pg_enum(enum_class: type[Enum], name: str) -> SAEnum:
    return SAEnum(
        enum_class,
        name=name,
        values_callable=lambda enum_type: [member.value for member in enum_type],
        validate_strings=True,
    )


