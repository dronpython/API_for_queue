import logging


class TaskTypeFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.task_type = "null" if not hasattr(record, "task_type") else record.task_type
        return True
