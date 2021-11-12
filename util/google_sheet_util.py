import gspread

default_file_name = "投资记录"

default_sheet_name = "基金投资详情"


def append_row(row, file_name=default_file_name, worksheet_name=default_sheet_name):
    get_ws(file_name, worksheet_name).append_row(row)


def append_rows(rows, file_name=default_file_name, worksheet_name=default_sheet_name):
    get_ws(file_name, worksheet_name).append_rows(rows)


def value_in_column(value, column, file_name=default_file_name, worksheet_name=default_sheet_name):
    ws = get_ws(file_name, worksheet_name)
    column_i_list = ws.get(f"{column}:{column}")
    return value in [r[0] for r in column_i_list]


def list_column(column, file_name=default_file_name, worksheet_name=default_sheet_name):
    list_of_lists = get_cells(column, file_name, worksheet_name)
    return [r[0] if r else "" for r in list_of_lists]


def get_cells(range_name, file_name=default_file_name, worksheet_name=default_sheet_name):
    return get_ws(file_name, worksheet_name).get(range_name)


def get_row_count(file_name=default_file_name, worksheet_name=default_sheet_name):
    """获取指定sheet页的总行数"""
    return get_ws(file_name, worksheet_name).row_count


def get_ws(file_name=default_file_name, worksheet_name=default_sheet_name):
    """获取指定的worksheet"""
    gc = gspread.service_account()
    sh = gc.open(file_name)
    return sh.worksheet(worksheet_name)
