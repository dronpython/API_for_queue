import logging
from contextvars import ContextVar

request_id: ContextVar[str] = ContextVar("request_id", default="service")


class RequestIdFilter(logging.Filter):
    """Добавление id запроса ко всем логам."""

    def filter(self, record):
        record.request_id = request_id.get()
        return True
