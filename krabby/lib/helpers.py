import pprint
import datetime
import time
from config import logger
# ____________________________


def generate_uid():

    return "%s.%s" %\
        (
            datetime.datetime.fromtimestamp(time.time()).strftime("%Y%m%d%H%M%S"),
            datetime.datetime.now().microsecond,
        )
# ____________________________


def calculate_date_range(ivt_days, duedate_include_weekends):
    days = []
    n = datetime.datetime.today()
    logger.debug("IVT DAYS: %d", ivt_days)
    logger.debug("TODAY: %r", n)
    logger.debug("Include weekends: %r", duedate_include_weekends)

    while len(days) < ivt_days:

        if duedate_include_weekends:
            days.append(n.date())
        else:
            if not n.weekday() in [4, 5]:
                logger.debug("Weekday: %r - including", n.weekday())
                days.append(n.date())

        n += datetime.timedelta(days=1)

    logger.debug("DAYS RANGE: {}".format(pprint.pformat(days)))
    return days[0], days[-1]
# ____________________________


def convert_to_utc(local_time):

    # NOTE. This is hard-coded for time-zones east to GMT

    local_str, offset_str = local_time.split('+')
    off_h, off_m = int(offset_str[:2]), int(offset_str[2:])

    offset = datetime.timedelta(hours=off_h, minutes=off_m)
    naive = datetime.datetime.strptime(local_str, "%Y-%m-%dT%H:%M:%S.%f")
    u = naive - offset
    return datetime.datetime.strftime(u, "%Y-%m-%d %H:%M")
# ____________________________
