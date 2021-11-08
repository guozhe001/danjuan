from unittest import TestCase
from util import http_util


class Test(TestCase):
    def test_parse_trade(self):
        baidu = http_util.get("https://www.baidu.com")
        print(baidu.text)
