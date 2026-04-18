from enum import Enum

from piccolo.columns import Varchar


def create_postgres_enum_type(db_type_name: str, enum: type[Enum]) -> type[Varchar]:
    """Factory function to create a PostgresEnum custom Piccolo column type"""

    class PostgresEnum(Varchar):
        def __init__(self, *args, **kwargs):
            self.db_type_name = db_type_name
            self.enum = enum
            kwargs["choices"] = enum

            super().__init__(*args, **kwargs)

        @property
        def column_type(self) -> str:
            return self.db_type_name

        def python_value(self, value):
            if self.enum and value is not None:
                return self.enum(value)
            return value

        def db_value(self, value):
            print(f"Converting {value} to db value for enum {self.enum}")
            if self.enum and isinstance(value, self.enum):
                return value.value
            return value

    return PostgresEnum
