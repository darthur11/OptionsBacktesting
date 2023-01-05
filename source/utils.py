import datetime
from enum import Enum
class dateFormats(Enum):
    ddmmyyyy_point = "%d.%m.%Y"
    ddmmyyyy_split = "%d/%m/%Y"
    yyyymmdd_dash = '%Y-%m-%d'

def convert_string_to_datetime(date_string: str, format: dateFormats) -> datetime.datetime:
    return datetime.datetime.strptime(date_string, format.value).replace(tzinfo=datetime.timezone.utc)

def convert_timestamp_to_datetime(ts_value: int):
    return datetime.datetime.fromtimestamp(ts_value, tz=datetime.timezone.utc)

