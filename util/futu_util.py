import datetime
import math

import futu as ft
import pandas as pd

from util import notify_util, num_util

api_svr_ip = '127.0.0.1'
api_svr_port = 11111

quote_ctx = ft.OpenQuoteContext(host=api_svr_ip, port=api_svr_port)

notify_count = {}


def get_stock_basicinfo(market, stock_type=ft.SecurityType.STOCK, code_list=None):
    ret_code, ret_data = quote_ctx.get_stock_basicinfo(market, stock_type, code_list)
    return ret_data if ret_code == 0 else []


def get_market_snapshot(stock_codes):
    ret_code, ret_data = quote_ctx.get_market_snapshot(stock_codes)
    return ret_data if ret_code == 0 else []


#
# def loop_get_mkt_snapshot(market: ft.Market, sub_type: ft.SecurityType):
#     """
#     验证接口：获取某个市场的全部快照数据 get_mkt_snapshot
#     :param market: market type
#     :return:
#     """
#     stock_codes = []
#     # 枚举所有的股票类型，获取股票codes
#     ret_code, ret_data = quote_ctx.get_stock_basicinfo(market, sub_type)
#     if ret_code == 0:
#         print("get_stock_basicinfo: market={}, sub_type={}, count={}".format(market, sub_type, len(ret_data)))
#         for ix, row in ret_data.iterrows():
#             print(row)
#             stock_codes.append(row['code'])
#
#     if len(stock_codes) == 0:
#         quote_ctx.close()
#         print("Error market:'{}' can not get stock info".format(market))
#         return

# 按频率限制获取股票快照: 每3秒200支股票
# for i in range(1, len(stock_codes), 200):
#     print("from {}, total {}".format(i, len(stock_codes)))
#     ret_code, ret_data = quote_ctx.get_market_snapshot(stock_codes[i:i + 200])
#     if ret_code == 0:
#         print(ret_data)
#     time.sleep(3)
#
# quote_ctx.close()


if __name__ == '__main__':
    basicinfo = get_stock_basicinfo(ft.Market.HK, ft.SecurityType.IDX, ["HK.800700"])
    print(type(basicinfo))
    print(basicinfo)

    if isinstance(basicinfo, pd.DataFrame):
        code = basicinfo["code"][0]
        name = basicinfo["name"][0]
    else:
        code = basicinfo[0]["code"]
        name = basicinfo[0]["name"]
    snapshot = get_market_snapshot([code])
    # row = snapshot[1]
    for key in snapshot:
        value = snapshot[key]
        print(key, value[0])
    last_price = snapshot["last_price"][0]
    prev_close_price = snapshot["prev_close_price"][0]
    rate = (last_price - prev_close_price) / prev_close_price
    print(prev_close_price, last_price, rate)
    if rate < -0.03 and notify_count[datetime.datetime.now().date()] < 5:
        notify_count[datetime.datetime.now().date()] += 1
    notify_util.notify_with_platform(f"{name}当前下跌超过3%, 下跌幅度:{round(rate * 100, 2)}%")
    #
    # for row in basicinfo.iterrows():
    #     # print(row["code"])
    #     # print(type(row))
    #     # print(row[1])
    #     data = row[1]
    #     # print(type(data))
    #     print(data["code"])
    #     print(row)
