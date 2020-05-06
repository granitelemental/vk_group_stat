from datetime import datetime

def date_from_timestamp(ts):
    return datetime.utcfromtimestamp(ts)