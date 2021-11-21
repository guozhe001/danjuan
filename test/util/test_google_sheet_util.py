import os
import socket
from datetime import datetime
from pathlib import PurePosixPath
from unittest import TestCase

import pandas as pd
import numpy as np
import socks

from util import google_sheet_util, financial, file_util, num_util, date_util

socks.set_default_proxy(socks.HTTP, "127.0.0.1", 8001)
socket.socket = socks.socksocket

fund_info_file_name = "fund_info.csv"


def get_fund_file_name(file_name="fund.csv"):
    return PurePosixPath(os.path.abspath(__file__)).parent.joinpath(file_name)


def delete_old_file_and_save_new(file_name, df):
    if file_util.exists(file_name):
        file_util.delete_file(file_name)
    df.to_csv(file_name, header=False, index=False)


class Test(TestCase):
    def test_print_xirr(self):
        # 测试
        data = [(datetime.date(2006, 1, 24), -39967), (datetime.date(2008, 2, 6), -19866),
                (datetime.date(2010, 10, 18), 245706), (datetime.date(2013, 9, 14), 52142)]
        print(financial.xirr(data))

    def test_value_in_column(self):
        result = google_sheet_util.value_in_column("391663853964445696", "I")
        self.assertFalse(result)

    def test_get_row_count(self):
        count = google_sheet_util.get_row_count()
        print(count)
        self.assertTrue(count > 0)

    def test_get_current_path(self):
        current_file_path = os.path.abspath(__file__)
        print(current_file_path)
        p = PurePosixPath(current_file_path)
        print(p.parent)
        print(type(p.parent))
        print(get_fund_file_name())

    def test_get_fund_data(self):
        columns = google_sheet_util.get_cells("A:J",
                                              value_render_option=google_sheet_util.ValueRenderOption.UNFORMATTED_VALUE,
                                              date_time_render_option=google_sheet_util.DateTimeRenderOption.FORMATTED_STRING)
        self.assertIsNotNone(columns)
        delete_old_file_and_save_new(get_fund_file_name(), pd.DataFrame(columns))

    def test_get_fund_info_data(self):
        columns = google_sheet_util.get_cells("A:E",
                                              value_render_option=google_sheet_util.ValueRenderOption.UNFORMATTED_VALUE,
                                              date_time_render_option=google_sheet_util.DateTimeRenderOption.FORMATTED_STRING,
                                              worksheet_name=google_sheet_util.fund_info_sheet_name)

        self.assertIsNotNone(columns)
        delete_old_file_and_save_new(get_fund_file_name(fund_info_file_name), pd.DataFrame(columns))

    def test_xirr(self):

        df = pd.read_csv(get_fund_file_name(), dtype=object, parse_dates=True,
                         infer_datetime_format=date_util.DATE_FORMAT)
        print(df.columns)
        df = df.fillna(value={google_sheet_util.FundHeaderName.tx_value: 0,
                              google_sheet_util.FundHeaderName.tx_price: 0,
                              google_sheet_util.FundHeaderName.tx_amount: 0,
                              google_sheet_util.FundHeaderName.tx_fees: 0})
        df_group_by = {}
        for row in df.values:
            code_data = df_group_by.get(row[2], [])
            code_data.append(row)
            df_group_by.setdefault(row[2], code_data)

        fund_info_df = pd.read_csv(get_fund_file_name(fund_info_file_name), header=1, dtype=str)
        print(fund_info_df.columns)
        print(fund_info_df.index)

        fund_code_amount_dict = {}
        for fund_code, rows in df_group_by.items():
            if rows:
                fund_code_amount_dict[fund_code] = max(sum(pd.DataFrame(rows)[:][6].astype(float)), 0)

        total_value = 0
        for row in fund_info_df.values:
            fund_code = row[0]
            fund_code_price = float(row[4])
            amount = num_util.round_floor(fund_code_amount_dict[fund_code], 4)
            fund_code_value = num_util.round_floor(fund_code_price * amount, 2)
            print(f"fund_code={fund_code}, fund_name={row[1]}, amount={amount}, price={fund_code_price}, "
                  f"fund_value={fund_code_value}")
            total_value += fund_code_value
        #
        total_value = num_util.round_floor(total_value, 2)
        print(total_value)

        dt_list = [date_util.str_to_datetime(dt_str, date_util.DATE_FORMAT) if isinstance(dt_str, str) else dt_str for
                   dt_str in df[google_sheet_util.FundHeaderName.action_date][1:]]
        cash_flow = list(zip(dt_list, [num_util.round_floor(float(amount), 2) for amount in
                                       df[google_sheet_util.FundHeaderName.tx_value][1:]]))
        cash_flow.append((datetime.now(), total_value))
        print(cash_flow)
        print(financial.xirr(list(cash_flow)))
