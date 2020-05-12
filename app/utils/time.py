from datetime import datetime, timezone

def date_from_timestamp(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc)