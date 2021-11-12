# encoding=utf8
import json

from util import google_sheet_util, danjuan_util


def write_to_google_sheet(rows):
    if rows:
        google_sheet_util.append_rows(rows)


def get_lasted_saved_order_id():
    # 记录父order_id的列
    column_order_id = google_sheet_util.list_column("J:J")
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


def main():
    saved_order_id = get_lasted_saved_order_id()
    # print(saved_order_id)
    lasted_saved_order_id = saved_order_id[len(saved_order_id) - 1]
    # print(f"lasted_saved_order_id={lasted_saved_order_id}")
    resp_dict_list = get_all(lasted_saved_order_id)
    data = get_success_and_not_save_data(resp_dict_list, lasted_saved_order_id)
    if data:
        write_to_google_sheet(danjuan_util.parse_trade(data, saved_order_id))
    print("蛋卷基金的数据已经全部写入到指定的google表格中")


if __name__ == "__main__":
    main()

# swap_order_id = "394203749278371840"
#
# amount, share, price, service_fee = danjuan_util.get_fund_swap_order_detail(swap_order_id)
# print(amount, share, price, service_fee)
#
# r = get(first_page)
# print(r.text)
