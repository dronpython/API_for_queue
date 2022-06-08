import logging


class TaskErrorsFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.task_errors = [] if not hasattr(record, "task_errors") else record.task_errors
        return True
