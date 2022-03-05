import json
import logging.handlers
import re


def fix_json(string: str, err: json.JSONDecodeError) -> str:
    unexpected_char = re.search(r'\(char (\d+)\)', str(err))
    if unexpected_char is not None:
        unexpected_char_position = int(unexpected_char.group(1))
        if unexpected_char_position == 0:
            string = f'"{string}"'
        else:
            # Most likely double quotes not escaped correctly
            unescaped_opening = string.rfind(r'"', 0, unexpected_char_position)
            string = string[:unescaped_opening] + r'\"' + string[unescaped_opening + 1:]
            unescaped_closing = string.find(r'"', unescaped_opening + 2)
            string = string[:unescaped_closing] + r'\"' + string[unescaped_closing + 1:]
    return string


def normalize_string(string_: str) -> str:
    # If cyrillic chars are in string it seems to be utf-8 encoded
    cyrillic_ = re.search(r'[\u0401\u0451\u0410-\u044f]+', string_)
    if cyrillic_ is None:
        string_ = string_.encode('ascii').decode('unicode_escape')
    return string_


class JSONSocketHandler(logging.handlers.SocketHandler):

    def emit(self, record: logging.LogRecord):
        record.msg = normalize_string(record.msg)
        try:
            record.msg = json.dumps(json.loads(record.msg), ensure_ascii=False)
        except json.JSONDecodeError:
            record.msg = json.dumps({"text": record.msg}, ensure_ascii=False)
        super().emit(record)
