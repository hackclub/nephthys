class TicketNotClosedError(Exception):
    def __init__(self, ticket_id: int):
        super().__init__("Cannot reopen a non-closed ticket")
        self.ticket_id = ticket_id
