from blockkit import Input
from blockkit import Modal
from blockkit import PlainTextInput


def get_configure_stale_days_modal(current_value: str | None = None):
    """
    Returns a modal for configuring the number of days before tickets are auto-closed as stale.

    Args:
        current_value: Current number of days (optional)
    """
    return Modal(
        title=":wrench: Stale Tickets",
        callback_id="configure_stale_days",
        submit=":white_check_mark: Save",
        blocks=[
            Input(
                label="Days before auto-close",
                block_id="stale_days",
                element=PlainTextInput(
                    action_id="stale_days",
                    placeholder="e.g. 7",
                    **({"initial_value": current_value} if current_value else {}),
                ),
                hint="Set the number of days of inactivity before a ticket is automatically closed. Leave empty to disable.",
                optional=True,
            ),
        ],
    ).build()
