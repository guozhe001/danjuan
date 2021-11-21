from unittest import TestCase
from constant import constant


class Test(TestCase):
    def test_parse_trade(self):
        print(constant.project_path)
        self.assertEqual("danjuan", constant.project_path)
