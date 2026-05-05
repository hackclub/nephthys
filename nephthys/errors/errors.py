class TicketNotClosedError(Exception):
    def __init__(self, ticket_id: int):
        super().__init__("Cannot reopen a non-closed ticket")
        self.ticket_id = ticket_id


class PermissionDenied(Exception):
    def __init__(self, message: str, user_id: int):
        super().__init__(message)
        self.user_id = user_id
