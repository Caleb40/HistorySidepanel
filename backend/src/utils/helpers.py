from datetime import datetime

import pytz


def get_utc_now():
    return datetime.now(pytz.UTC)
