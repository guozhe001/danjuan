from unittest import TestCase

from util import google_sheet_util


class Test(TestCase):
    def test_value_in_column(self):
        result = google_sheet_util.value_in_column("391663853964445696", "I")
        self.assertFalse(result)

    def test_get_row_count(self):
        count = google_sheet_util.get_row_count()
        print(count)
        self.assertTrue(count > 0)

    def test_append_row(self):
        row = [1629268603, "买入", "501009", "汇添富中证生物科技指数A", -55.14, 2.5774, 21.37, 0.06, "394203749160931328"]
        google_sheet_util.append_row(row)
