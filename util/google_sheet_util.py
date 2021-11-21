import gspread

default_file_name = "投资记录"

default_sheet_name = "基金投资详情"

fund_info_sheet_name = "投资品种"


class ValueRenderOption:
    """
    Values will be calculated & formatted in the reply according to the cell's formatting.
    Formatting is based on the spreadsheet's locale, not the requesting user's locale.
    For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "$1.23".
    """
    FORMATTED_VALUE = "FORMATTED_VALUE"
    """Values will be calculated, but not formatted in the reply. 
    For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return the number 1.23.
    """
    UNFORMATTED_VALUE = "UNFORMATTED_VALUE"
    """Values will not be calculated. The reply will include the formulas. 
    For example, if A1 is 1.23 and A2 is =A1 and formatted as currency, then A2 would return "=A1".
    """
    FORMULA = "FORMULA"


class DateTimeRenderOption:
    """
    Instructs date, time, datetime, and duration fields to be output as doubles in "serial number" format,
    as popularized by Lotus 1-2-3.
    The whole number portion of the value (left of the decimal) counts the days since December 30th 1899.
    The fractional portion (right of the decimal) counts the time as a fraction of the day.
    For example, January 1st 1900 at noon would be 2.5, 2 because it's 2 days after December 30st 1899,
    and .5 because noon is half a day. February 1st 1900 at 3pm would be 33.625.
    This correctly treats the year 1900 as not a leap year.
    """
    SERIAL_NUMBER = "SERIAL_NUMBER"
    """
    Instructs date, time, datetime, and duration fields to be output as strings in their given number format 
    (which is dependent on the spreadsheet locale).
    """
    FORMATTED_STRING = "FORMATTED_STRING"


class FundHeaderName:
    action_date = "日期"
    action_type = "操作（买/卖）"
    fund_code = "交易品种代码"
    fund_name = "交易品种"
    tx_value = "交易金额（元）"
    tx_price = "成交单价（元）"
    tx_amount = "交易份额"
    tx_fees = "手续费"


def append_row(row, file_name=default_file_name, worksheet_name=default_sheet_name):
    get_ws(file_name, worksheet_name).append_row(row)


def append_rows(rows, file_name=default_file_name, worksheet_name=default_sheet_name):
    get_ws(file_name, worksheet_name).append_rows(rows)


def value_in_column(value, column, file_name=default_file_name, worksheet_name=default_sheet_name):
    ws = get_ws(file_name, worksheet_name)
    column_i_list = ws.get(f"{column}:{column}")
    return value in [r[0] for r in column_i_list]


def get_column(column, file_name=default_file_name, worksheet_name=default_sheet_name):
    """获取制定的一列数据"""
    list_of_lists = get_cells(column, file_name, worksheet_name)
    return [r[0] if r else "" for r in list_of_lists]


def get_cells(range_name, file_name=default_file_name, worksheet_name=default_sheet_name,
              value_render_option=ValueRenderOption.FORMATTED_VALUE,
              date_time_render_option=DateTimeRenderOption.SERIAL_NUMBER):
    """获取制定的所有单元格数据，返回结果为list of list"""
    return get_ws(file_name, worksheet_name).get(range_name, value_render_option=value_render_option,
                                                 date_time_render_option=date_time_render_option)


def get_row_count(file_name=default_file_name, worksheet_name=default_sheet_name):
    """获取指定sheet页的总行数"""
    return get_ws(file_name, worksheet_name).row_count


def get_ws(file_name=default_file_name, worksheet_name=default_sheet_name):
    """获取指定的worksheet"""
    gc = gspread.service_account()
    sh = gc.open(file_name)
    return sh.worksheet(worksheet_name)
