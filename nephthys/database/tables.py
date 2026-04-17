from piccolo.columns import Boolean
from piccolo.columns import Column
from piccolo.columns import ForeignKey
from piccolo.columns import OnDelete
from piccolo.columns import OnUpdate
from piccolo.columns import Text
from piccolo.columns import Timestamp
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.table import Table


class User(Table):
    slack_id = Text(db_column_name="slackId")
    username = Text(null=True)
    admin = Boolean(default=False)
    helper = Boolean(default=False)

    opened_tickets = ForeignKey(references="Ticket")
    closed_tickets = ForeignKey(references="Ticket")
    assigned_tickets = ForeignKey(references="Ticket")
    reopened_tickets = ForeignKey(references="Ticket")

    created_category_tags = ForeignKey(references="CategoryTag")
    created_at = Timestamp(default=TimestampNow())


class Ticket(Table):
    title = Text()
    description = Text()
    status = Column()  # TODO: Enum

    msg_ts = Text(db_column_name="msgTs", unique=True)
    ticket_ts = Text(db_column_name="ticketTs", unique=True)
    user_facing_msgs = ForeignKey(references="BotMessage")  # TODO

    last_msg_at = Timestamp(default=TimestampNow())
    last_msg_by = Column()  # TODO: Enum

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

    assigned_at = Timestamp(null=True)
    reopened_at = Timestamp(null=True)

    team_tags = ForeignKey(references="TeamTag", db_column_name="tagsOnTickets")
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
    created_at = Timestamp(default=TimestampNow())


class QuestionTag(Table):
    label = Text(unique=True)
    tickets = ForeignKey(references=Ticket)
    created_at = Timestamp(default=TimestampNow())


class TeamTag(Table, tablename="Tag"):
    name = Text(unique=True)
    created_at = Timestamp(default=TimestampNow())


class CategoryTag(Table):
    name = Text(unique=True)
    created_by = ForeignKey(references=User, db_column_name="createdById", null=True)
    created_at = Timestamp(default=TimestampNow())


class BotMessage(Table):
    ts = Text()
    channel_id = Text(db_column_name="channelId")
    ticket = ForeignKey(
        references=Ticket, db_column_name="ticketId", on_delete=OnDelete.cascade
    )
    # Unimplemented: ts + channel_id should be unique together


class TagsOnTickets(Table):
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
    assigned_at = Timestamp(default=TimestampNow())


class UserTagSubscription(Table):
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
    subscribed_at = Timestamp(default=TimestampNow())
