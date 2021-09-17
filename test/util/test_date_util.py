from unittest import TestCase
from util import date_util


class Test(TestCase):
    def test_format_unix_datetime(self):
        datetime = date_util.format_unix_datetime(date_util.DAY_FORMAT, 1629268603170)
        print(datetime)
        print(type(datetime))
