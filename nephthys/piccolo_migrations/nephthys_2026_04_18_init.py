from enum import Enum

from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.base import OnDelete
from piccolo.columns.base import OnUpdate
from piccolo.columns.column_types import Boolean
from piccolo.columns.column_types import ForeignKey
from piccolo.columns.column_types import Serial
from piccolo.columns.column_types import Text
from piccolo.columns.column_types import Timestamp
from piccolo.columns.defaults.timestamp import TimestampNow
from piccolo.columns.indexes import IndexMethod
from piccolo.table import Table

from nephthys.database.enums import TicketStatusColumn
from nephthys.database.enums import UserTypeColumn
from nephthys.database.tables import UserTagSubscription


class TeamTag(Table, tablename="Tag", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=True,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class Ticket(Table, tablename="Ticket", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=True,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class User(Table, tablename="User", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=True,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class CategoryTag(Table, tablename="CategoryTag", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=True,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


class QuestionTag(Table, tablename="QuestionTag", schema=None):
    id = Serial(
        null=False,
        primary_key=True,
        unique=True,
        index=False,
        index_method=IndexMethod.btree,
        choices=None,
        db_column_name=None,
        secret=False,
    )


ID = "2026-04-18T14:12:56:828491"
VERSION = "1.33.0"
DESCRIPTION = "Initial database state before we adopted Piccolo"


# Dummy table we use to execute raw SQL with:
class RawTable(Table):
    pass


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="nephthys", description=DESCRIPTION
    )

    async def before():
        await RawTable.raw(
            """CREATE TYPE ticket_status AS ENUM ('OPEN', 'IN_PROGRESS', 'CLOSED');"""
        )
        await RawTable.raw(
            """CREATE TYPE user_type AS ENUM ('AUTHOR', 'HELPER', 'OTHER');"""
        )

    manager.add_raw(before)

    manager.add_table(
        class_name="TagsOnTickets",
        tablename="tags_on_tickets",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="BotMessage", tablename="BotMessage", schema=None, columns=None
    )

    manager.add_table(class_name="TeamTag", tablename="Tag", schema=None, columns=None)

    manager.add_table(
        class_name="Ticket", tablename="Ticket", schema=None, columns=None
    )

    manager.add_table(class_name="User", tablename="User", schema=None, columns=None)

    manager.add_table(
        class_name="CategoryTag",
        tablename="CategoryTag",
        schema=None,
        columns=None,
    )

    manager.add_table(
        class_name="QuestionTag",
        tablename="QuestionTag",
        schema=None,
        columns=None,
    )

    manager.add_column(
        table_class_name="TagsOnTickets",
        tablename="tags_on_tickets",
        column_name="ticket",
        db_column_name="ticketId",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Ticket,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "ticketId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TagsOnTickets",
        tablename="tags_on_tickets",
        column_name="tag",
        db_column_name="tagId",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": TeamTag,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": True,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "tagId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TagsOnTickets",
        tablename="tags_on_tickets",
        column_name="assigned_at",
        db_column_name="assignedAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "assignedAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="BotMessage",
        tablename="BotMessage",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="BotMessage",
        tablename="BotMessage",
        column_name="ts",
        db_column_name="ts",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="BotMessage",
        tablename="BotMessage",
        column_name="channel_id",
        db_column_name="channelId",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "channelId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="BotMessage",
        tablename="BotMessage",
        column_name="ticket",
        db_column_name="ticketId",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": Ticket,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "ticketId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TeamTag",
        tablename="Tag",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TeamTag",
        tablename="Tag",
        column_name="name",
        db_column_name="name",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="TeamTag",
        tablename="Tag",
        column_name="created_at",
        db_column_name="createdAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "createdAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="title",
        db_column_name="title",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="description",
        db_column_name="description",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="status",
        db_column_name="status",
        column_class_name="TicketStatusColumn",
        column_class=TicketStatusColumn,
        params={
            "length": 255,
            "default": "OPEN",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": Enum(
                "TicketStatus",
                {
                    "OPEN": "OPEN",
                    "IN_PROGRESS": "IN_PROGRESS",
                    "CLOSED": "CLOSED",
                },
            ),
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="msg_ts",
        db_column_name="msgTs",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "msgTs",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="ticket_ts",
        db_column_name="ticketTs",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "ticketTs",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="last_msg_at",
        db_column_name="lastMsgAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "lastMsgAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="last_msg_by",
        db_column_name="lastMsgBy",
        column_class_name="UserTypeColumn",
        column_class=UserTypeColumn,
        params={
            "length": 255,
            "default": "AUTHOR",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": Enum(
                "UserType",
                {"AUTHOR": "AUTHOR", "HELPER": "HELPER", "OTHER": "OTHER"},
            ),
            "db_column_name": "lastMsgBy",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="opened_by",
        db_column_name="openedById",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.restrict,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "openedById",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="reopened_by",
        db_column_name="reopenedById",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.set_null,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "reopenedById",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="closed_by",
        db_column_name="closedById",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.set_null,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "closedById",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="assigned_to",
        db_column_name="assignedToId",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.set_null,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "assignedToId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="assigned_at",
        db_column_name="assignedAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "assignedAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="closed_at",
        db_column_name="closedAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "closedAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="reopened_at",
        db_column_name="reopenedAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "reopenedAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="question_tag",
        db_column_name="questionTagId",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": QuestionTag,
            "on_delete": OnDelete.set_null,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "questionTagId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="category_tag",
        db_column_name="categoryTagId",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": CategoryTag,
            "on_delete": OnDelete.set_null,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "categoryTagId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="Ticket",
        tablename="Ticket",
        column_name="created_at",
        db_column_name="createdAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "createdAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="User",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="User",
        column_name="slack_id",
        db_column_name="slackId",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "slackId",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="User",
        column_name="username",
        db_column_name="username",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="User",
        column_name="admin",
        db_column_name="admin",
        column_class_name="Boolean",
        column_class=Boolean,
        params={
            "default": False,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="User",
        column_name="helper",
        db_column_name="helper",
        column_class_name="Boolean",
        column_class=Boolean,
        params={
            "default": False,
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="User",
        tablename="User",
        column_name="created_at",
        db_column_name="createdAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "createdAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="CategoryTag",
        tablename="CategoryTag",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="CategoryTag",
        tablename="CategoryTag",
        column_name="name",
        db_column_name="name",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="CategoryTag",
        tablename="CategoryTag",
        column_name="created_by",
        db_column_name="createdById",
        column_class_name="ForeignKey",
        column_class=ForeignKey,
        params={
            "references": User,
            "on_delete": OnDelete.cascade,
            "on_update": OnUpdate.cascade,
            "target_column": None,
            "null": True,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "createdById",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="CategoryTag",
        tablename="CategoryTag",
        column_name="created_at",
        db_column_name="createdAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "createdAt",
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="QuestionTag",
        tablename="QuestionTag",
        column_name="id",
        db_column_name="id",
        column_class_name="Serial",
        column_class=Serial,
        params={
            "null": False,
            "primary_key": True,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="QuestionTag",
        tablename="QuestionTag",
        column_name="label",
        db_column_name="label",
        column_class_name="Text",
        column_class=Text,
        params={
            "default": "",
            "null": False,
            "primary_key": False,
            "unique": True,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": None,
            "secret": False,
        },
        schema=None,
    )

    manager.add_column(
        table_class_name="QuestionTag",
        tablename="QuestionTag",
        column_name="created_at",
        db_column_name="createdAt",
        column_class_name="Timestamp",
        column_class=Timestamp,
        params={
            "default": TimestampNow(),
            "null": False,
            "primary_key": False,
            "unique": False,
            "index": False,
            "index_method": IndexMethod.btree,
            "choices": None,
            "db_column_name": "createdAt",
            "secret": False,
        },
        schema=None,
    )

    async def after():
        # Piccolo doesn't support composite keys
        # https://github.com/piccolo-orm/piccolo/issues/1379
        await UserTagSubscription.raw("""
            CREATE TABLE "user_tag_subscriptions" (
                "userId" INTEGER NOT NULL REFERENCES "User"(id) ON DELETE CASCADE ON UPDATE CASCADE,
                "tagId" INTEGER NOT NULL REFERENCES "Tag"(id) ON DELETE CASCADE ON UPDATE CASCADE,
                "subscribedAt" TIMESTAMP NOT NULL DEFAULT current_timestamp,
                PRIMARY KEY ("userId", "tagId")
            );
        """)

        # Manually add composite uniqueness constraints, because they're not
        # built in to Piccolo yet
        # await BotMessage.raw(
        #     """CREATE UNIQUE INDEX "BotMessage_ts_channelId_key" ON "BotMessage"("ts", "channelId");"""
        # )

    manager.add_raw(after)

    return manager
