import logging


class TaskSubtypeFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.task_subtype = "null" if not hasattr(record, "task_subtype") else record.task_subtype
        return True
