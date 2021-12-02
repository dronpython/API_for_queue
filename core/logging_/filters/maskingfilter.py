import logging
from logging import LogRecord
import re
from typing import List


class MaskingFilter(logging.Filter):

    def __init__(self, mask: str, patterns: List[str]):
        super().__init__()
        self._mask = mask
        self._patterns = patterns

    def filter(self, record: LogRecord):
        record.msg = self.redact(record.msg)
        if isinstance(record.args, dict):
            for k in record.args.keys():
                record.args[k] = self.redact(record.args[k])
        else:
            record.args = tuple(self.redact(arg) for arg in record.args)
        return True

    def redact(self, msg: str):
        msg = isinstance(msg, str) and msg or str(msg)
        for pattern in self._patterns:
            msg = re.sub(pattern, self._mask, msg, flags=re.IGNORECASE)
        if msg.isdigit():
            msg = int(msg)
        return msg
