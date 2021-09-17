import gspread

gc = gspread.service_account()

sh = gc.open("投资记录")

# print(sh.sheet1.get('A1'))
# worksheet_list = sh.worksheets()
# for worksheet in worksheet_list:
#     print(worksheet)

ws = sh.worksheet("基金投资详情")
column_i_list = ws.get("H:H")
print(type(column_i_list))
column_i = [r[0] for r in column_i_list]
print(type(column_i))
for r in column_i:
    print(r)
# 这个不是有数据的行数，而是这个sheet页的所有行数，包括空行
# print(ws.row_count)
# print(ws.get('A1'))
# list_of_lists = ws.get_all_values()
# for row in list_of_lists:
#     print(row)
# for cell in row:
#     print(cell)
