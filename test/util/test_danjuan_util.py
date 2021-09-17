from unittest import TestCase
from util import danjuan_util


class Test(TestCase):
    def test_parse_trade(self):
        swap_order_id = "394203749278371840"
        amount, share, price, service_fee = danjuan_util.get_fund_buy_order_detail(swap_order_id)
        print(amount, share, price, service_fee)
