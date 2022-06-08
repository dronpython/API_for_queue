import logging


class TaskSystemFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.task_system = "null" if not hasattr(record, "task_system") else record.task_system
        return True
