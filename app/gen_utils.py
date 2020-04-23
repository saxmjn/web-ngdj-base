from datetime import datetime, timedelta
import pytz
import re

def convertBoolean(bool_str):
    if bool_str.lower() == 'false':
        return False
    elif bool_str.lower() == 'true':
        return True
    else:
        return None

########################### DateTime #################################


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

########################### Email, Phone #################################
def check_for_valid_email(email):
    if not email:
        return False
    if re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
        return True
    else:
        return False


def check_for_valid_phone(phone):
    if not phone:
        return False
    elif phone == '':
        return False
    else:
        return True