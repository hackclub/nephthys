from blockkit import Header
from blockkit import Home
from blockkit import Section
from blockkit.core import ModalBlock


def error_screen(header: list[ModalBlock], title: str, message: str) -> dict:
    """A basic error screen that can be rendered as a view if permissions are missing, or something like that"""
    return Home(
        [
            *header,
            Header(title),
            Section(message),
        ]
    ).build()
