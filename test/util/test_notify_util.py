from unittest import TestCase
from util import notify_util


class Test(TestCase):
    def test_parse_trade(self):
        notify_util.notify_with_platform("test")
