import logging
from contextvars import ContextVar

endpoint: ContextVar[str] = ContextVar("endpoint", default="null")


class EndpointFilter(logging.Filter):
    """Добавление endpoint запроса ко всем логам."""

    def filter(self, record):
        record.endpoint = endpoint.get()
        return True
