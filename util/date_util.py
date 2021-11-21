import math
from datetime import datetime, time

import dateutil
import dateutil.parser
import pytz
from tzlocal import get_localzone

date_format = '%Y-%m-%d %H:%M:%S'

DATE_FORMAT_T = "YYYY-MM-DDTHH:%M:%S.%f"

date_format_1 = '%Y%m%d%H%M%S'

DATE_FORMAT = '%Y-%m-%d'

TIME_ZONE = "Asia/Shanghai"


# 判断给定的参数是否是'%Y-%m-%d %H:%M'格式的时间
def is_date(s):
    try:
        dt = datetime.strptime(s, '%Y-%m-%d %H:%M')
        return dt, True
    except TypeError:
        return None, False
    except ValueError:
        return None, False


def format_unix_datetime(format_pattern, unix_timestamp):
    """
    格式化unix时间戳

    Args:
      format_pattern (str): 目标日期格式
      unix_timestamp (int): Unix 时间戳，毫秒

    Returns:
      格式化后的字符串
    """
    return format_unix_datetime_from_second(format_pattern, int(unix_timestamp / 1000))


def format_unix_datetime_from_second(format_pattern, utc_timestamp):
    """
    格式化unix时间戳

    Args:
      format_pattern (str): 目标日期格式
      utc_timestamp (int): Unix 时间戳, 单位秒

    Returns:
      格式化后的字符串
    """
    temp_dt = datetime.utcfromtimestamp(utc_timestamp)
    utc_tz = pytz.timezone('UTC')

    # 将时区变更为 utc 时区
    utc_dt = temp_dt.replace(tzinfo=utc_tz)

    # 转化为上海时区时间
    shanghai_dt = utc_dt.astimezone(pytz.timezone(TIME_ZONE))  # 直接转带时区的时间

    return shanghai_dt.strftime(format_pattern)


# unix_timestamp参数的单位是毫秒：1603227600000
def format_default_datetime(unix_timestamp):
    return format_unix_datetime(date_format, unix_timestamp)


# unix_timestamp参数的单位是秒：1603227600
def timestamp_to_str(timestamp):
    return format_default_datetime(int(timestamp) * 1000)


def get_now_timestamp_second() -> int:
    """
    获取当前时间的时间戳，精确到秒
    :return:  当前时间的时间戳
    """
    return math.floor(get_now_timestamp())


def get_now_timestamp() -> float:
    """
    获取当前时间的时间戳，个位数是秒，小数点后有数字
    :return:  当前时间的时间戳
    """
    return datetime.now().timestamp()


def interval_hours(date1: datetime, date2: datetime):
    """
    获取两个时间的间隔小时数
    :param date1:
    :param date2:
    :return: 如果date1在date2之后，则返回值大于等于0，否则返回值小于0
    """
    sub = date1 - date2
    return int((sub.days * 24 * 3600 + sub.seconds) / 3600)


def interval(date1: datetime, date2: datetime, period=3600):
    """
    获取两个时间的间隔小时数, 如果date1比date2小，则返回负数
    :param date1:
    :param date2:
    :param period:  单位是秒，即间隔多少秒
    :return: 如果date1在date2之后，则返回值大于等于0，否则返回值小于0
    """
    sub = date1 - date2
    return int((sub.days * 24 * 3600 + sub.seconds) / period)


def str_to_datetime(s, format_pattern=date_format):
    return datetime.strptime(s, format_pattern)


def str_to_timestamp(s, format_pattern=date_format):
    return int(datetime.strptime(s, format_pattern).timestamp())


def utc_str_to_date(date_str):
    announcement_time = dateutil.parser.parse(date_str)
    if announcement_time.tzname() == 'UTC':
        tz = get_localzone()  # 获得本地timezone
        announcement_time = announcement_time.astimezone(tz)
    return announcement_time


def get_start_time_of_day(dt: datetime):
    return dt.replace(dt.year, dt.month, dt.day, 0, 0, 0, 0)


def is_same_day(date1: datetime, date2: datetime):
    return date1.year == date2.year and date1.month == date2.month and date1.day == date2.day


def is_same_minute(date1: datetime, date2: datetime):
    return date1.year == date2.year and date1.month == date2.month and date1.day == date2.day and \
           date1.hour == date2.hour and date1.minute == date2.minute


def to_start_of_day(d: datetime):
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def date_to_str(d: datetime, format_pattern=date_format) -> str:
    return d.strftime(format_pattern)


def is_zero_time(dt):
    """是否是零点"""
    return dt.time() == time(hour=0, minute=0, second=0)
