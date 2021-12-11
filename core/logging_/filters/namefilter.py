import logging


class AppFilter(logging.Filter):
    def filter(self, record):
        record.source = 'qservice'
        return True
