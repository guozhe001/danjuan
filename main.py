# encoding=utf8
import argparse
import json
from datetime import datetime

import pandas as pd

from constant import constant
from util import google_sheet_util, danjuan_util, date_util, file_util, num_util, financial
from util.google_sheet_util import FundHeaderName, DateTimeRenderOption, ValueRenderOption

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
    lasted_saved_index = 0
    first_not_success_index = len(items)
    for i in range(len(items)):
        if _lasted_saved_order_id == items[i].get("order_id"):
            lasted_saved_index = i
        if items[i].get("status") == "new":
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


def get_newest_fund_data(file_name, df):
    if file_util.exists(file_name):
        file_util.delete_file(file_name)
    df.to_csv(file_name, header=False, index=False)


def get_fund_file_name(file_name=constant.FundFileName.fund_file_name):
    return constant.project_path.joinpath("data", file_name)


def get_all_newest_fund_data():
    # 投资记录
    columns = google_sheet_util.get_cells("A:J",
                                          value_render_option=ValueRenderOption.UNFORMATTED_VALUE,
                                          date_time_render_option=DateTimeRenderOption.FORMATTED_STRING)
    df = pd.DataFrame(columns)
    df = df.fillna(value={FundHeaderName.tx_value: 0,
                          FundHeaderName.tx_price: 0,
                          FundHeaderName.tx_amount: 0,
                          FundHeaderName.tx_fees: 0})
    get_newest_fund_data(get_fund_file_name(), df)
    # 基金信息，包括当前价格
    columns = google_sheet_util.get_cells("A:E",
                                          value_render_option=ValueRenderOption.UNFORMATTED_VALUE,
                                          date_time_render_option=DateTimeRenderOption.FORMATTED_STRING,
                                          worksheet_name=google_sheet_util.fund_info_sheet_name)
    get_newest_fund_data(get_fund_file_name(constant.FundFileName.fund_info_file_name), pd.DataFrame(columns))


def do_analysis_single_fund(fund_code, fund_code_price, rows, fund_name):
    if rows:
        fund_df = pd.DataFrame(rows)
        dt_list = [date_util.str_to_datetime(dt_str, date_util.DATE_FORMAT) if isinstance(dt_str, str) else dt_str
                   for dt_str in fund_df[0]]
        fund_code_value_list = [num_util.round_floor(float(amount), 2) for amount in fund_df[4]]
        cash_flow = list(zip(dt_list, fund_code_value_list))
        amount = num_util.round_floor(
            max(sum([num_util.round_floor(float(amount), 2) for amount in fund_df[6]]), 0), 4) if rows else 0
        fund_code_value = num_util.round_floor(fund_code_price * amount, 2)
        cash_flow.append((datetime.now(), fund_code_value))
        if fund_code_value + sum(fund_code_value_list) >= 0:
            print(f"基金代码={fund_code}, 基金名称={fund_name}, 当前持有份额={amount}, 每份价格={fund_code_price}, "
                  f"当前总价值={fund_code_value}, xirr复合年化收益率={num_util.round_floor(financial.xirr(list(cash_flow)) * 100, 2)}%")
        else:
            print(f"基金代码={fund_code}, 基金名称={fund_name}, 当前持有份额={amount}, 每份价格={fund_code_price}, "
                  f"当前总价值={fund_code_value}, 亏损={round(fund_code_value + sum(fund_code_value_list), 2)}")
        return fund_code_value
    return 0


def do_analysis():
    df = pd.read_csv(get_fund_file_name(), dtype=object)
    df = df.fillna({FundHeaderName.tx_value: 0, FundHeaderName.tx_price: 0, FundHeaderName.tx_amount: 0,
                    FundHeaderName.tx_fees: 0})

    fund_info_df = pd.read_csv(get_fund_file_name(constant.FundFileName.fund_info_file_name), header=1, dtype=str)

    total_value = num_util.round_floor(sum([do_analysis_single_fund(fund_info[0], float(fund_info[4]),
                                                                    [fund_detail for fund_detail in df.values if
                                                                     fund_detail[2] == fund_info[0]],
                                                                    fund_info[1]) for fund_info in
                                            fund_info_df.values]), 2)
    dt_list = [date_util.str_to_datetime(dt_str, date_util.DATE_FORMAT) if isinstance(dt_str, str) else dt_str for
               dt_str in df[FundHeaderName.action_date][1:]]
    cash_flow = list(zip(dt_list, [num_util.round_floor(float(amount), 2) for amount in
                                   df[FundHeaderName.tx_value][1:]]))
    cash_flow.append((datetime.now(), total_value))

    bid_value = round(sum([v for v in df[FundHeaderName.tx_value][1:].astype(float) if v < 0]), 2)
    redeem_value = round(sum([v for v in df[FundHeaderName.tx_value][1:].astype(float) if v > 0]), 2)
    print(f"从【{df[FundHeaderName.action_date][0]}】截止到【{datetime.now().date()}】, "
          f"总申购金额={bid_value}, 总赎回+分红金额={redeem_value}, 当前持有基金份额总价值={total_value}, "
          f"总盈利={round(total_value + redeem_value + bid_value, 2)}, "
          f"xirr复合年化收益率={num_util.round_floor(financial.xirr(list(cash_flow)) * 100, 2)}%")


def analysis_fund():
    """分析基金投资的数据"""
    # 1、下载基金投资数据
    # get_all_newest_fund_data()
    # 2、计算每个基金以及汇总的收益：总投资额度、止盈金额、目前市值、当前浮盈/浮亏（金额和百分比）、xirr年化收益率
    do_analysis()


def main():
    args = parser.parse_args()
    add_proxy(args.proxy_host, args.proxy_port)
    # if args.sync_danjuan:
    #     write_danjuan_to_google_sheet()
    if args.analysis:
        analysis_fund()


if __name__ == "__main__":
    main()
