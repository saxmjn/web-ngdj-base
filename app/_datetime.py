from datetime import date, datetime, timedelta
import pytz

today = datetime.combine(date.today(), datetime.min.time())
tomorrow = today + timedelta(days=1)
now = datetime.now()


def to_epoch(datetime_iso, timezone=None):
    datetime_obj = create_datetime_from_iso(datetime_iso)
    base_datetime_obj = create_datetime(1970, 1, 1)
    epoch_time = (datetime_obj - base_datetime_obj).total_seconds()
    return epoch_time


def get_datetime(date):
    import datetime
    arr = date.split('-')
    return datetime.datetime(year=int(arr[0]), month=int(arr[1]), day=int(arr[2]))


def get_datetime_str(date):
    return '{}-{}-{}'.format(date.year, '{date:%m}', '{date:%d}')



def create_datetime(year, month, day, timezone=None):
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = tz.localize(datetime(year, month, day))
    return date_time


def create_datetime_from_iso(datetime_str, timezone=None):
    if datetime_str is None or datetime_str is '':
        return None
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = tz.localize(datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%fZ'), is_dst=None)
    return date_time


def create_datetime_from_str(datetime_str, format, timezone=None):
    """
    '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S%z',
    :param datetime_str:
    :param timezone:
    :return:
    """
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = tz.localize(datetime.strptime(datetime_str, format), is_dst=None)
    return date_time


def current_datetime(timezone=None):
    if timezone:
        tz = pytz.timezone(timezone)
    else:
        tz = pytz.utc

    date_time = datetime.now(tz)
    return date_time


def yesterday_datetime(timezone=None):
    now = datetime.now()
    return create_datetime(now.year, now.month, now.day, timezone=timezone) - timedelta(days=1)


def today_datetime(timezone=None):
    now = datetime.now()
    return create_datetime(now.year, now.month, now.day, timezone=timezone)


def tomorrow_datetime(timezone=None):
    now = datetime.now()
    return create_datetime(now.year, now.month, now.day, timezone=timezone) + timedelta(days=1)


def utc_to_user_datetime(date_time, timezone):
    """
    Converts the datetime obj from User Timezone to UTC
    :param date_time: aware_utc_dt_obj
    :param timezone: user timezone
    :return:
    """
    return date_time.astimezone(pytz.timezone(timezone))


def stringify_utc_to_user_datetime(date_time, timezone):
    """
    :param date_time:
    :param timezone:
    :return:
    """
    return date_time.astimezone(pytz.timezone(timezone)).strftime("%Y-%m-%dT%H:%M:%S")


def user_to_utc_datetime(date_time):
    """
    Converts the datetime obj from UTC to User Timezone
    :param date_time: aware_user_timezone_dt_obj
    :return:
    """
    return date_time.astimezone(pytz.utc)


def stringify_user_to_utc_datetime(date_time):
    """
    :param date_time:
    :param timezone:
    :return:
    """
    return date_time.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%S")


def strp_to_user_datetime(datetime_str, timezone):
    unaware = datetime.strptime(datetime_str[:19], "%Y-%m-%dT%H:%M:%S")
    tz_obj = pytz.timezone(timezone)
    return tz_obj.localize(unaware)


def strp_to_utc_datetime(datetime_str, timezone=None):
    unaware = datetime.strptime(datetime_str[:19], "%Y-%m-%dT%H:%M:%S")
    if timezone:
        datetime_in_timezone = pytz.timezone(timezone).localize(unaware)
        datetime_in_utc = datetime_in_timezone.astimezone(pytz.utc)
    else:
        datetime_in_utc = pytz.utc.localize(unaware)
    return datetime_in_utc


def timediff_hrs(start, end):
    x = (end - start)
    x = x.total_seconds() / 3600
    return x