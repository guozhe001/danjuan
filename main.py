# encoding=utf8
import argparse
import json
from datetime import datetime

from util import google_sheet_util, danjuan_util, date_util
import pandas as pd

# 定义入参
parser = argparse.ArgumentParser()
parser.add_argument("--proxy_port", help="代理端口", type=int, default=10808)
parser.add_argument("--proxy_host", help="代理host", default="127.0.0.1")
parser.add_argument("--sync_danjuan", help="是否同步蛋卷基金到google表格", type=bool, default=True)
parser.add_argument("--analysis", help="是否分析基金投资数据", type=bool, default=False)


def add_proxy(proxy_host, proxy_port):
    import socket
    import socks
    socks.set_default_proxy(socks.SOCKS5, proxy_host, proxy_port)
    socket.socket = socks.socksocket


def write_to_google_sheet(rows):
    if rows:
        google_sheet_util.append_rows(rows)


def get_lasted_saved_order_id():
    # 记录父order_id的列
    column_order_id = google_sheet_util.get_column("J:J")
    # print(column_order_id)
    # print(type(column_order_id))
    # 最后一条order_id
    return [order_id for order_id in column_order_id if order_id != '']
    # return '391663853964445696'


def get_all(_lasted_saved_order_id):
    i = 1
    result = []
    while i > 0:
        resp = danjuan_util.get(danjuan_util.list_orders_url_template.format(i, danjuan_util.page_size))
        resp_dict = json.loads(resp.text)
        # print(resp_dict)
        result.append(resp_dict)
        order_ids = danjuan_util.parse_trade_all(resp_dict)
        if _lasted_saved_order_id in order_ids:
            break
        i += 1
    return result


def get_success_and_not_save_data(result, _lasted_saved_order_id):
    items = []
    for resp_dict in result:
        for item in resp_dict.get("data").get("items"):
            items.append(item)

    items = sorted(items, key=lambda item: item["created_at"])
    # lambda i: i['age'])
    # for item in items:
    #     print(item)
    lasted_saved_index = 0
    first_not_success_index = len(items)
    for i in range(len(items)):
        if _lasted_saved_order_id == items[i].get("order_id"):
            lasted_saved_index = i
        if items[i].get("status") == "new":
            # print(items[i])
            first_not_success_index = i
            break
    return items[lasted_saved_index + 1:first_not_success_index]


def write_danjuan_to_google_sheet():
    saved_order_id = get_lasted_saved_order_id()
    # print(saved_order_id)
    lasted_saved_order_id = saved_order_id[len(saved_order_id) - 1]
    # print(f"lasted_saved_order_id={lasted_saved_order_id}")
    resp_dict_list = get_all(lasted_saved_order_id)
    data = get_success_and_not_save_data(resp_dict_list, lasted_saved_order_id)
    now_str = datetime.now().strftime(date_util.date_format)
    if data:
        write_to_google_sheet(danjuan_util.parse_trade(data, saved_order_id))
        print(f"{now_str}-已将蛋卷基金的{len(data)}条数据写入到指定的google表格中")
    else:
        print(f"{now_str}-没有需要更新的数据")


def analysis_fund():
    """分析基金投资的数据"""
    # 1、下载基金投资数据
    # 2、计算每个基金以及汇总的收益：总投资额度、止盈金额、目前市值、当前浮盈/浮亏（金额和百分比）、xirr年化收益率
    cells = google_sheet_util.get_cells("A:H")
    df = pd.DataFrame(cells)
    df.to_csv("./jupyter/fund.csv", header=False, index=False)


def main():
    args = parser.parse_args()
    add_proxy(args.proxy_host, args.proxy_port)
    # if args.sync_danjuan:
    #     write_danjuan_to_google_sheet()
    if args.analysis:
        analysis_fund()


if __name__ == "__main__":
    main()
