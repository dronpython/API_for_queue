import logging


class TaskMessageFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.task_message = "null" if not hasattr(record, "task_message") else record.task_message
        return True
