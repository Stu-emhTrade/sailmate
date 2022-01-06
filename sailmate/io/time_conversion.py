import pytz
from datetime import datetime

# todo we should grab the timezone (or offset) from the OS

def convert_to_utc(ts: datetime) -> datetime:
    nzt = pytz.timezone('Pacific/Auckland')
    ts = nzt.localize(ts).astimezone(pytz.utc)
    return ts
