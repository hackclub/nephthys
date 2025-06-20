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
from typing import Annotated, Generic, Optional, Self, TypeVar
from prisma.types import TicketWhereInput
import strawberry
from strawberry.dataloader import DataLoader
from strawberry.asgi import GraphQL
from base64 import b64encode, b64decode
from pydantic import BaseModel
from nephthys.utils.env import env
import prisma.models as models

T = TypeVar("T")

# Data loaders

async def tag_loader_fn(keys: list[int]) -> list[Tag | ValueError]:
    tag_list = await env.db.tag.find_many(
        where={
            "id": {"in": keys}
        }
    )

    tag_map = {tag.id: Tag.from_model(tag) for tag in tag_list}

    return [tag_map.get(key, ValueError("not found")) for key in keys]

tag_loader = DataLoader(load_fn=tag_loader_fn)


async def ticket_loader_fn(keys: list[int]) -> list[Ticket | ValueError]:
    ticket_list = await env.db.ticket.find_many(
        where={
            "id": {"in": keys}
        }
    )

    ticket_map = {ticket.id: Ticket.from_model(ticket) for ticket in ticket_list}

    return [ticket_map.get(key, ValueError("not found")) for key in keys]

ticket_loader = DataLoader(load_fn=ticket_loader_fn)


async def user_loader_fn(keys: list[int]) -> list[User | ValueError]:
    user_list = await env.db.user.find_many(
        where={
            "id": {"in": keys}
        }
    )

    user_map = {user.id: User.from_model(user) for user in user_list}

    return [user_map.get(key, ValueError("not found")) for key in keys]

user_loader = DataLoader(load_fn=user_loader_fn)


class Cursor(BaseModel):
    ns: str
    id: int

    def serialise(self) -> str:
        return b64encode(self.model_dump_json().encode()).decode()

    @classmethod
    def deserialise(cls, serialised: str | None) -> Self | None:
        return cls.model_validate_json(b64decode(serialised)) \
            if serialised is not None else None


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


@strawberry.type
class Extension:
    name: str
    version: str


@strawberry.type
class SupportKitMetadata:
    interface_version: str = "v0.2025.06.16"
    extensions: list[Extension] = dataclasses.field(default_factory=list)


@strawberry.input
class Search:
    text_search: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


@strawberry.type
class Tag:
    id: strawberry.ID
    name: str

    @strawberry.field
    def tickets(
        self,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[Ticket]:
        ...

    @classmethod
    def from_model(cls, model: models.Tag):
        return cls(
            id=strawberry.ID(str(model.id)),
            name=model.name
        )


@strawberry.enum
class TicketState(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


@strawberry.type
class Ticket:
    id: strawberry.ID
    name: str
    state: TicketState

    thread_id: str
    
    opened_by_id: strawberry.Private[int]
    
    @strawberry.field
    async def opened_by(self) -> User:
        return await user_loader.load(self.opened_by_id)

    @strawberry.field
    def tags(
        self,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[Tag]:
        ...

    @classmethod
    def from_model(cls, model: models.Ticket):
        return cls(
            id=strawberry.ID(str(model.id)),
            opened_by_id=model.openedById,
            name=model.description,
            state=TicketState.OPEN if model.status == "OPEN" else TicketState.CLOSED,
            thread_id=model.ticketTs
        )


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
    def tickets(
        self,
        query: Optional[Search] = None,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[Ticket]:
        ...

    @strawberry.field
    def tags(
        self,
        query: Optional[Search] = None,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[Tag]:
        ...

    @classmethod
    def from_model(cls, model: models.User):
        return cls(
            id=strawberry.ID(str(model.id)),
            slack_id=strawberry.ID(model.slackId),
            type=UserType.AGENT if model.helper else UserType.USER
        )


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
    def ticket_search(
        self,
        query: Search,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[Ticket]:
        ...

    @strawberry.field
    def tag_search(
        self,
        query: Search,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[Tag]:
        ...

    @strawberry.field
    def user_search(
        self,
        query: Search,
        after: Optional[strawberry.ID] = None,
        before: Optional[strawberry.ID] = None,
        first: Optional[int] = None, 
        last: Optional[int] = None
    ) -> Page[User]:
        ...


@strawberry.type
class Mutation:
    @strawberry.field
    def set_ticket_state(
        self,
        id: strawberry.ID,
        state: TicketState
    ) -> Ticket:
        ...

    @strawberry.field
    def set_ticket_tags(
        self,
        id: strawberry.ID,
        tags: list[strawberry.ID]
    ) -> Ticket:
        ...


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation
)

graphql = GraphQL(
    schema=schema,
    allow_queries_via_get=False
)
