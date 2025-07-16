"""
Implements some of the SupportKit GraphQL specification using Strawberry.

The rest is Slack-specific and is meant to be resolved using federation
with an external resolver.

See README.md for more information.
"""

from __future__ import annotations
import dataclasses
from datetime import datetime
import enum
import logging
from typing import Annotated, Any, Callable, Generic, Optional, Self, TypeVar
from prisma.types import TicketWhereInput
import strawberry
from strawberry.dataloader import DataLoader
from strawberry.asgi import GraphQL
from base64 import b64encode, b64decode
from pydantic import BaseModel
from nephthys.actions.resolve import resolve
from nephthys.utils.env import env
import prisma.models as models

T = TypeVar("T")

logger = logging.getLogger(__name__)


# ===
# DATA LOADERS


async def tag_loader_fn(keys: list[int]) -> list[Tag | ValueError]:
    tag_list = await env.db.tag.find_many(where={"id": {"in": keys}})

    tag_map = {tag.id: Tag.from_model(tag) for tag in tag_list}

    return [tag_map.get(key, ValueError("not found")) for key in keys]


tag_loader = DataLoader(load_fn=tag_loader_fn)


async def ticket_loader_fn(keys: list[int]) -> list[Ticket | ValueError]:
    ticket_list = await env.db.ticket.find_many(where={"id": {"in": keys}})

    ticket_map = {ticket.id: Ticket.from_model(ticket) for ticket in ticket_list}

    return [ticket_map.get(key, ValueError("not found")) for key in keys]


ticket_loader = DataLoader(load_fn=ticket_loader_fn)


async def user_loader_fn(keys: list[int]) -> list[User | ValueError]:
    user_list = await env.db.user.find_many(where={"id": {"in": keys}})

    user_map = {user.id: User.from_model(user) for user in user_list}

    return [user_map.get(key, ValueError("not found")) for key in keys]


user_loader = DataLoader(load_fn=user_loader_fn)


# ===
# PAGINATION


class Cursor(BaseModel):
    ns: str
    id: int

    def serialise(self) -> str:
        return b64encode(self.model_dump_json().encode()).decode()

    @classmethod
    def deserialise(cls, serialised: str | None) -> Self | None:
        return (
            cls.model_validate_json(b64decode(serialised))
            if serialised is not None
            else None
        )


@strawberry.type
class PageInfo:
    has_next_page: bool
    has_previous_page: bool
    start_cursor: Optional[strawberry.ID] = None
    end_cursor: Optional[strawberry.ID] = None


@strawberry.type
class Edge(Generic[T]):
    cursor: strawberry.ID
    node: T


@strawberry.type
class Page(Generic[T]):
    count: int
    edges: list[Edge[T]]
    page_info: PageInfo

    @classmethod
    async def paginate[D: models.Ticket | models.Tag | models.User, E](
        cls,
        db_query: dict,
        db: type[D],
        db_to_model: Callable[[D], E],
        ns: str,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[E]:
        # Assert that one of first or last isn't None
        assert (first is not None) != (last is not None)

        after_cursor = Cursor.deserialise(after)
        before_cursor = Cursor.deserialise(before)

        if after_cursor and before_cursor:
            db_query["id"] = {"gt": after_cursor.id, "lt": before_cursor.id}
        elif after_cursor:
            db_query["id"] = {"lt": after_cursor.id}
        elif before_cursor:
            db_query["id"] = {"gt": before_cursor.id}

        fetch_count = (first or last or 0) + 1
        logger.info(f"graphql pagination fetch query: {db_query}")
        tickets = await db.prisma().find_many(
            take=fetch_count,
            order={"id": "desc" if first else "asc"},
            where=db_query,  # type: ignore
        )
        logger.info(f"fetched: {tickets}")

        if last is not None:
            pass

        if db_query.get("id"):
            del db_query["id"]

        count = await db.prisma().count(
            where=db_query  # type: ignore
        )

        return Page(
            count=count,
            edges=[
                Edge(
                    cursor=strawberry.ID(Cursor(ns=ns, id=edge.id).serialise()),
                    node=db_to_model(edge),
                )
                for edge in tickets[: (first or last or 0)]
            ],
            page_info=PageInfo(
                # It has a next page if we fetched all N + 1 items, we were paging forwards
                # OR if we were paging backwards, since there would've been a previous page
                has_next_page=((len(tickets) == fetch_count) and (first is not None))
                or (before is not None),
                has_previous_page=((len(tickets) == fetch_count) and (last is not None))
                or (after is not None),
                # The start cursor and end cursor are the cursors of the first and last elements in the edges
                start_cursor=strawberry.ID(Cursor(ns=ns, id=tickets[0].id).serialise())
                if len(tickets) > 0
                else None,
                end_cursor=strawberry.ID(
                    Cursor(
                        ns=ns,
                        id=tickets[min(len(tickets), (first or last or 0)) - 1].id,
                    ).serialise()
                )
                if len(tickets) > 0
                else None,
            ),
        )


@strawberry.input
class Search:
    text_search: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None

    def to_query(self, fts_column: str) -> dict[str, Any]:
        query = dict()

        if self.from_date and self.to_date:
            query["createdAt"] = {"lt": self.to_date, "gt": self.from_date}
        elif self.from_date:
            query["createdAt"] = {"gt": self.from_date}
        elif self.to_date:
            query["createdAt"] = {"lt": self.to_date}

        if self.text_search:
            query[fts_column] = {"search": self.text_search.lower()}

        return query


# ===
# TICKETS AND TAGS


@strawberry.type
class Tag:
    id: strawberry.ID
    name: str

    @strawberry.field
    async def tickets(
        self,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[Ticket]:
        return await Page.paginate(
            db_query={"tagsOnTickets": {"some": {"tagId": int(self.id)}}},
            db=models.Ticket,
            db_to_model=Ticket.from_model,
            ns=f"/tag/{self.id}/tickets_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )

    @classmethod
    def from_model(cls, model: models.Tag):
        return cls(id=strawberry.ID(str(model.id)), name=model.name)


@strawberry.enum
class TicketState(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


@strawberry.type
class Ticket:
    id: strawberry.ID
    name: str
    state: TicketState

    public_thread_id: str
    private_thread_id: str

    opened_by_id: strawberry.Private[int]
    model: strawberry.Private[models.Ticket]

    @strawberry.field
    async def opened_by(self) -> User:
        return await user_loader.load(self.opened_by_id)

    @strawberry.field
    async def tags(
        self,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[Tag]:
        return await Page.paginate(
            db_query={"ticketsOnTags": {"some": {"ticketId": int(self.id)}}},
            db=models.Tag,
            db_to_model=Tag.from_model,
            ns=f"/ticket/{self.id}/tags_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )

    @classmethod
    def from_model(cls, model: models.Ticket):
        return cls(
            id=strawberry.ID(str(model.id)),
            opened_by_id=model.openedById,
            name=model.description,
            state=TicketState.OPEN if model.status == "OPEN" else TicketState.CLOSED,
            public_thread_id=f"{env.slack_help_channel}/{model.msgTs}",
            private_thread_id=f"{env.slack_ticket_channel}/{model.ticketTs}",
            model=model,
        )


# ===
# USERS AND MESSAGES


@strawberry.type
class UserMetadata:
    profile_picture: Optional[str] = None
    about: Optional[str] = None
    pronouns: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[int] = None


@strawberry.enum
class UserType(enum.Enum):
    AGENT = "agent"
    USER = "user"


@strawberry.type
class User:
    id: strawberry.ID
    slack_id: strawberry.ID
    type: UserType

    @strawberry.field
    async def tickets(
        self,
        query: Optional[Search] = None,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[Ticket]:
        db_query = {"openedById": int(self.id)}

        if query:
            query_filters = query.to_query(fts_column="description")
            db_query.update(query_filters)

        return await Page.paginate(
            db_query=db_query,
            db=models.Ticket,
            db_to_model=Ticket.from_model,
            ns=f"/user/{self.id}/tickets_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )

    @strawberry.field
    async def tags(
        self,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[Tag]:
        db_query = {"userSubscriptions": {"some": {"userId": int(self.id)}}}

        return await Page.paginate(
            db_query=db_query,
            db=models.Tag,
            db_to_model=Tag.from_model,
            ns=f"/user/{self.id}/tags_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )

    @classmethod
    def from_model(cls, model: models.User):
        return cls(
            id=strawberry.ID(str(model.id)),
            slack_id=strawberry.ID(model.slackId),
            type=UserType.AGENT if model.helper else UserType.USER,
        )


# ===
# QUERIES AND MUTATIONS


@strawberry.type
class Extension:
    name: str
    version: str


@strawberry.type
class SupportKitMetadata:
    interface_version: str = "v0.2025.06.16"
    extensions: list[Extension] = dataclasses.field(default_factory=list)


@strawberry.type
class Query:
    @strawberry.field(name="_supportkitMetadata")
    def metadata(self) -> SupportKitMetadata:
        return SupportKitMetadata()

    @strawberry.field
    async def ticket(self, id: strawberry.ID) -> Ticket:
        return await ticket_loader.load(int(id))

    @strawberry.field
    async def tag(self, id: strawberry.ID) -> Tag:
        return await tag_loader.load(int(id))

    @strawberry.field
    async def user(self, id: strawberry.ID) -> User:
        return await user_loader.load(int(id))

    @strawberry.field
    async def ticket_search(
        self,
        query: Search,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[Ticket]:
        return await Page.paginate(
            db_query=query.to_query(fts_column="name"),
            db=models.Ticket,
            db_to_model=Ticket.from_model,
            ns="/ticket_search_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )

    @strawberry.field
    async def tag_search(
        self,
        query: Search,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[Tag]:
        return await Page.paginate(
            db_query=query.to_query(fts_column="name"),
            db=models.Tag,
            db_to_model=Tag.from_model,
            ns="/tag_search_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )

    @strawberry.field
    async def user_search(
        self,
        query: Search,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None,
        last: Optional[int] = None,
    ) -> Page[User]:
        return await Page.paginate(
            db_query=query.to_query(fts_column="username"),
            db=models.User,
            db_to_model=User.from_model,
            ns="/user_search_v0",
            after=after,
            before=before,
            first=first,
            last=last,
        )


@strawberry.type
class Mutation:
    @strawberry.field
    async def resolve_ticket(self, id: strawberry.ID, by: strawberry.ID) -> Ticket:
        ticket = await ticket_loader.load(int(id))

        await resolve(ticket.model.msgTs, resolver=by, client=env.slack_client)

        ticket_loader.clear(int(id))
        return await ticket_loader.load(int(id))

    @strawberry.field
    def set_ticket_tags(
        self, id: strawberry.ID, tags: list[strawberry.ID]
    ) -> Ticket: ...


schema = strawberry.Schema(query=Query, mutation=Mutation)

graphql = GraphQL(
    schema=schema, allow_queries_via_get=False, debug=env.environment == "development"
)
