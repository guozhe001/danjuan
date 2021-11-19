from unittest import TestCase
from util import file_util

md_image_temp = "![report]({}/{}/report.png)"


def print_(base_path):
    paths = file_util.list_all_sub_path(base_path)
    sorted_paths = sorted([sub_path.name for sub_path in paths])
    for sub_path_name in sorted_paths:
        print(md_image_temp.format(base_path, sub_path_name))


class Test(TestCase):

    def test_list_all_sub_path(self):
        eth_have_risk = "/Users/apple/Desktop/fairy/eth"
        eth_no_risk = "/Users/apple/Desktop/fairy/fairy_strat_no_risk/eth"
        print_(eth_have_risk)

    def test_list_all_sub_path_btc(self):
        # btc_no_risk_path = '/Users/apple/Desktop/fairy/fairy_strat_no_risk/BTC_USDT'
        btc_have_risk_path = '/Users/apple/Desktop/fairy/btc'
        print_(btc_have_risk_path)
