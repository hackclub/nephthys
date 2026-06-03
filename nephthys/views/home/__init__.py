from enum import Enum


class AppHomeView(Enum):
    id: str
    label: str

    DASHBOARD = "dashboard", "Dashboard"
    ASSIGNED_TICKETS = "assigned-tickets", "Assigned Tickets"
    TEAM_TAGS = "team-tags", "Team Tags"
    CATEGORY_TAGS = "category-tags", "Category Tags"
    MY_STATS = "my-stats", "My Stats"

    def __new__(cls, id: str, label: str):
        member = object.__new__(cls)
        member._value_ = id
        member.id = id
        member.label = label
        return member
