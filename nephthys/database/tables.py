from datetime import datetime

from piccolo.columns import Boolean
from piccolo.columns import ForeignKey
from piccolo.columns import OnDelete
from piccolo.columns import Text
from piccolo.columns import Timestamptz
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
    # tag subscriptions
    created_at = Timestamptz(auto_update=datetime.now)


class Ticket(Table):
    title = Text()
    description = Text()
    # status = None  # TODO: Enum

    msg_ts = Text(db_column_name="msgTs", unique=True)
    ticket_ts = Text(db_column_name="ticketTs", unique=True)
    user_facing_msgs = ForeignKey(references="BotMessage")  # TODO

    last_msg_at = Timestamptz(auto_update=datetime.now)
    # last_msg_by = None  # TODO: Enum

    opened_by = ForeignKey(references=User, db_column_name="openedById")
    reopened_by = ForeignKey(references=User, db_column_name="reopenedById", null=True)
    closed_by = ForeignKey(references=User, db_column_name="closedById", null=True)
    assigned_to = ForeignKey(references=User, db_column_name="assignedToId", null=True)

    team_tags = ForeignKey(references="TeamTag", db_column_name="tagsOnTickets")
    question_tag = ForeignKey(
        references="QuestionTag", db_column_name="questionTagId", null=True
    )
    category_tag = ForeignKey(
        references="CategoryTag", db_column_name="categoryTagId", null=True
    )
    created_at = Timestamptz(auto_update=datetime.now)


class QuestionTag(Table):
    name = Text(unique=True)
    created_at = Timestamptz(auto_update=datetime.now)


class TeamTag(Table, tablename="Tag"):
    name = Text(unique=True)
    user_subscriptions = ForeignKey(
        references="UserTagSubscription", db_column_name="userSubscriptions"
    )
    created_at = Timestamptz(auto_update=datetime.now)


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
    assigned_at = Timestamptz(auto_update=datetime.now)


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
    subscribed_at = Timestamptz(auto_update=datetime.now)


class BotMessage(Table):
    ts = Text()
    channel_id = Text(db_column_name="channelId")
    ticket = ForeignKey(
        references=Ticket, db_column_name="ticketId", on_delete=OnDelete.cascade
    )
    # Unimplemented: ts + channel_id should be unique together


class CategoryTag(Table):
    name = Text(unique=True)
    created_by = ForeignKey(references=User, db_column_name="createdById", null=True)
    created_at = Timestamptz(auto_update=datetime.now)
