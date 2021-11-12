from datetime import datetime
from unittest import TestCase

from util import google_sheet_util, financial, date_util
import pandas as pd

import socket
import socks

socks.set_default_proxy(socks.HTTP, "127.0.0.1", 8001)
socket.socket = socks.socksocket


class Test(TestCase):
    def test_value_in_column(self):
        result = google_sheet_util.value_in_column("391663853964445696", "I")
        self.assertFalse(result)

    def test_get_row_count(self):
        count = google_sheet_util.get_row_count()
        print(count)
        self.assertTrue(count > 0)

    def test_list_columns(self):
        columns = google_sheet_util.get_cells("A:J")
        print(type(columns))
        for c in columns:
            print(c)
        df = pd.DataFrame(columns)
        xirr = financial.xirr(zip([datetime.strptime(dt_str, date_util.DAY_FORMAT) for dt_str in df[0][1:]], df[4][1:]))
        print(xirr)

    # def test_append_row(self):
    #     row = [1629268603, "买入", "501009", "汇添富中证生物科技指数A", -55.14, 2.5774, 21.37, 0.06, "394203749160931328"]
    #     google_sheet_util.append_row(row)
