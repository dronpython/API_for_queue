import logging


class TicketIdFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.ticket_id = "null" if not hasattr(record, "ticket_id") else record.ticket_id
        return True
