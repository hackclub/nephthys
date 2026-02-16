from dataclasses import dataclass


@dataclass
class View:
    name: str
    id: str
    # Not today
    # render: Callable[[User | None], dict]


APP_HOME_VIEWS: list[View] = [
    View("Dashboard", "dashboard"),
    View("Assigned Tickets", "assigned-tickets"),
    View("Team Tags", "team-tags"),
    View("My Stats", "my-stats"),
]
