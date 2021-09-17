from datetime import datetime

import math
import pytz

date_format = '%Y-%m-%d %H:%M:%S'

DATE_FORMAT_T = "YYYY-MM-DDTHH:%M:%S.%f"

TIME_ZONE = "Asia/Shanghai"

DAY_FORMAT = '%Y-%m-%d'


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


# unix_timestamp参数的单位是毫秒：1603227600000
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
    print(date1, date2)
    sub = date1 - date2
    print(sub.seconds)
    print(sub.days)
    print(sub.seconds)
    return int((sub.days * 24 * 3600 + sub.seconds) / 3600)
