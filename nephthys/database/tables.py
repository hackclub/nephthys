from enum import StrEnum

from piccolo.columns import Boolean
from piccolo.columns import ForeignKey
from piccolo.columns import LazyTableReference
from piccolo.columns import M2M
from piccolo.columns import OnDelete
from piccolo.columns import OnUpdate
from piccolo.columns import Serial
from piccolo.columns import Text
from piccolo.columns import Timestamp
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.table import Table

from nephthys.database.postgres_enum import PostgresEnum


class TicketStatus(StrEnum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class UserType(StrEnum):
    AUTHOR = "AUTHOR"
    HELPER = "HELPER"
    OTHER = "OTHER"


def table_ref(table: str) -> LazyTableReference:
    """Shorthand for the LazyTableReference constructor."""
    return LazyTableReference(table, module_path=__name__)


class User(Table, tablename="User"):
    id = Serial(primary_key=True, unique=True)
    slack_id = Text(db_column_name="slackId")
    username = Text(null=True)
    admin = Boolean(default=False)
    helper = Boolean(default=False)

    team_tag_subscriptions = M2M(table_ref("UserTagSubscription"))

    created_at = Timestamp(default=TimestampNow(), db_column_name="createdAt")


class Ticket(Table, tablename="Ticket"):
    id = Serial(primary_key=True, unique=True)
    title = Text()
    description = Text()
    status = PostgresEnum("TicketStatus", TicketStatus)

    msg_ts = Text(db_column_name="msgTs", unique=True)
    ticket_ts = Text(db_column_name="ticketTs", unique=True)

    last_msg_at = Timestamp(default=TimestampNow(), db_column_name="lastMsgAt")
    last_msg_by = PostgresEnum(
        "UserType", UserType, default=UserType.AUTHOR, db_column_name="lastMsgBy"
    )

    opened_by = ForeignKey(
        references=User,
        db_column_name="openedById",
        on_delete=OnDelete.restrict,
        on_update=OnUpdate.cascade,
    )
    reopened_by = ForeignKey(
        references=User,
        db_column_name="reopenedById",
        null=True,
        on_delete=OnDelete.set_null,
        on_update=OnUpdate.cascade,
    )
    closed_by = ForeignKey(
        references=User,
        db_column_name="closedById",
        null=True,
        on_delete=OnDelete.set_null,
        on_update=OnUpdate.cascade,
    )
    assigned_to = ForeignKey(
        references=User,
        db_column_name="assignedToId",
        null=True,
        on_delete=OnDelete.set_null,
        on_update=OnUpdate.cascade,
    )

    assigned_at = Timestamp(null=True, db_column_name="assignedAt")
    closed_at = Timestamp(null=True, db_column_name="closedAt")
    reopened_at = Timestamp(null=True, db_column_name="reopenedAt")

    team_tags = M2M(table_ref("TagsOnTickets"))
    question_tag = ForeignKey(
        references="QuestionTag",
        db_column_name="questionTagId",
        null=True,
        on_delete=OnDelete.set_null,
        on_update=OnUpdate.cascade,
    )
    category_tag = ForeignKey(
        references="CategoryTag",
        db_column_name="categoryTagId",
        null=True,
        on_delete=OnDelete.set_null,
        on_update=OnUpdate.cascade,
    )
    created_at = Timestamp(default=TimestampNow(), db_column_name="createdAt")


class QuestionTag(Table, tablename="QuestionTag"):
    id = Serial(primary_key=True, unique=True)
    label = Text(unique=True)
    created_at = Timestamp(default=TimestampNow(), db_column_name="createdAt")


class TeamTag(Table, tablename="Tag"):
    id = Serial(primary_key=True, unique=True)
    name = Text(unique=True)
    created_at = Timestamp(default=TimestampNow(), db_column_name="createdAt")

    tag_subscriptions = M2M(table_ref("UserTagSubscription"))
    tickets = M2M(table_ref("TagsOnTickets"))


class CategoryTag(Table, tablename="CategoryTag"):
    id = Serial(primary_key=True, unique=True)
    name = Text(unique=True)
    created_by = ForeignKey(references=User, db_column_name="createdById", null=True)
    created_at = Timestamp(default=TimestampNow(), db_column_name="createdAt")


class BotMessage(Table, tablename="BotMessage"):
    id = Serial(primary_key=True, unique=True)
    ts = Text()
    channel_id = Text(db_column_name="channelId")
    ticket = ForeignKey(
        references=Ticket, db_column_name="ticketId", on_delete=OnDelete.cascade
    )
    # Unimplemented: ts + channel_id should be unique together


class TagsOnTickets(Table, tablename="tags_on_tickets"):
    ticket = ForeignKey(
        references=Ticket,
        db_column_name="ticketId",
        primary_key=True,
        on_delete=OnDelete.cascade,
    )
    tag = ForeignKey(
        references=TeamTag,
        db_column_name="tagId",
        primary_key=True,
        on_delete=OnDelete.cascade,
    )
    assigned_at = Timestamp(default=TimestampNow(), db_column_name="assignedAt")


class UserTagSubscription(Table, tablename="user_tag_subscriptions"):
    user = ForeignKey(
        references=User,
        db_column_name="userId",
        primary_key=True,
        on_delete=OnDelete.cascade,
    )
    tag = ForeignKey(
        references=TeamTag,
        db_column_name="tagId",
        primary_key=True,
        on_delete=OnDelete.cascade,
    )
    subscribed_at = Timestamp(default=TimestampNow(), db_column_name="subscribedAt")
