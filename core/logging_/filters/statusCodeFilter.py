import logging


class StatusCodeFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.status_code = "NULL" if not hasattr(record, "status_code") else record.status_code
        return True
