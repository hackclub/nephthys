from enum import StrEnum

from nephthys.database.postgres_enum import create_postgres_enum_type


class TicketStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class UserType(StrEnum):
    AUTHOR = "AUTHOR"
    HELPER = "HELPER"
    OTHER = "OTHER"


TicketStatusColumn = create_postgres_enum_type("TicketStatus", TicketStatus)
UserTypeColumn = create_postgres_enum_type("UserType", UserType)
