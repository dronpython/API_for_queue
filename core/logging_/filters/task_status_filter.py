import logging


class TaskStatusFilter(logging.Filter):
    """Добавляет источник логов."""
    def filter(self, record):
        record.task_status = "null" if not hasattr(record, "task_status") else record.task_status
        return True
