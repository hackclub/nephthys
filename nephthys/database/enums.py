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


class FeedbackRating(StrEnum):
    GREAT = "GREAT"
    OKAY = "OKAY"
    NOT_GOOD = "NOT_GOOD"


FeedbackRatingColumn = create_postgres_enum_type("feedback_rating", FeedbackRating)
# Note: these database type names were PascalCase in the Prisma era,
# but we have a migration to make them snake_case for consistency and Piccolo compatibility.
TicketStatusColumn = create_postgres_enum_type("ticket_status", TicketStatus)
UserTypeColumn = create_postgres_enum_type("user_type", UserType)
