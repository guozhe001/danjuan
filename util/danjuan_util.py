import json
from pathlib import Path

from util import file_util, http_util, date_util

# Utilities
PROJECT_PACKAGE = Path(__file__).resolve().parent.parent

cookie = file_util.read_file(PROJECT_PACKAGE.joinpath('cookie.txt'))[0]

headers = {"Accept": "application/json, text/plain, */*",
           "Accept-Encoding": "gzip, deflate, br",
           "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7",
           "Connection": "keep-alive",
           "Cookie": str(cookie),
           "elastic-apm-traceparent": "00-4f39113c11fa6311020a549faf85dcf8-dadf02fc81ec425e-01",
           "Host": "danjuanapp.com",
           "Referer": "https://danjuanapp.com/trade-record",
           # "sec-ch-ua": """"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"""",
           "sec-ch-ua-mobile": "?0",
           "Sec-Fetch-Dest": "empty",
           "Sec-Fetch-Mode": "cors",
           "Sec-Fetch-Site": "same-origin",
           "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
           }

# trade_record_url = "https://danjuanapp.com/trade-record"
page_size = 20
# https://danjuanapp.com/djapi/order/p/list?page=1&size=20&type=all

list_orders_url_template = "https://danjuanapp.com/djapi/order/p/list?page={}&size={}&type=all"
first_page = list_orders_url_template.format(1, page_size)

order_detail = "https://danjuanapp.com/djapi/fund/order/{}"

# https://danjuanapp.com/djmodule/trade-details?ordertype=fund&orderid=397121338216634368
fund_trade_detail = "https://danjuanapp.com/djmodule/trade-details?ordertype=fund&orderid={}"

plan_order_detail = "https://danjuanapp.com/djapi/order/p/plan/{}"

# 页面的URL是：https://danjuanapp.com/djmodule/trade-details?ordertype=fund&orderid=397121338216634368
# 打开上面页面的url之后会请求：https://danjuanapp.com/djapi/plan/order/394203749387423744
plan_trade_detail = "https://danjuanapp.com/plan-trade-detail?orderid={}"

# 在这个歌订单之前的数据已经记录，这个订单以及之前的数据不再记录
last_order_id = "391663853964445696"


class DanjuanType:
    plan = "plan"
    fund = "fund"


class DanjuanAction:
    swap = "036"
    swap_out = "038"
    swap_in = "037"
    buy = "022"
    # 分红
    dividend = "143"


positive_and_negative = {DanjuanAction.swap_out: 1, DanjuanAction.swap_in: -1, DanjuanAction.buy: -1,
                         DanjuanAction.dividend: 1}


def get(url):
    return http_util.get_with_headers(url, headers)


def get_fund_buy_order_detail(order_id):
    order_detail_resp = get(order_detail.format(order_id))
    order_detail_text = order_detail_resp.text
    # {"data": {"order_type_name": "申购", "order_id": "394205816253137920", "fd_code": "519671", "fd_name": "银河沪深300价值指数",
    #           "amount": "317.00", "volume": "0.00", "confirm_amount": 317, "confirm_volume": 197.89,
    #           "status": "success", "channel": "b", "action": "022", "if_undo": "n", "bankcard_no": "6214********2565",
    #           "bank_name": "招商银行", "bank_serial": "007", "confirm_date": 1628611200000, "query_date": 1628697600000,
    #           "created_at": 1628573488584, "updated_at": 0, "status_desc": "申购完成", "action_desc": "买入", "step": 3,
    #           "undo_tip": "撤单后资金预计在8月12日19点前退回到银行卡，你确定撤单吗？", "tips": [], "confirm_infos": [
    #         ["确认信息", "确认金额,317.00元", "确认份额,197.89份", "确认净值,1.6000", "净值日期,2021-08-10", "确认日期,2021-08-11", "手续费,0.38元"]],
    #           "ttype": "fund", "state_msg": "交易系统受理成功，等待基金公司确认", "cycle_flag": false, "confirm_flag": false,
    #           "desc": ["支付成功，将按08-10日净值确认份额", "2021-08-10 13:31:28", "基金公司确认份额，开始计算收益", "2021-08-11", "查询收益",
    #                    "2021-08-12 18:00前"], "real_rate": 0.12}, "result_code": 0}
    order_detail_text = json.loads(order_detail_text)
    data = order_detail_text.get("data")
    confirm_infos = data.get("confirm_infos")
    negative_or_negative = positive_and_negative.get(data.get("action"))
    confirm_info = confirm_infos[0]
    amount = str(data.get("confirm_amount") * negative_or_negative)
    # 如果金额是负则说明是买入，那么份额是正；否则金额是正，说明是卖出，则份额是负
    share = str(data.get("confirm_volume") * negative_or_negative * -1)
    price = confirm_info[3].split(",")[1]
    service_fee = confirm_info[len(confirm_info) - 1].split(",")[1][:-1]
    return amount, share, price, service_fee


def parse_fund(item):
    """解析基金"""
    order_id = item.get("order_id")
    amount, share, price, service_fee = get_fund_buy_order_detail(order_id)
    # {'order_id': '397121338216634368', 'uid': 284893233, 'code': '519671', 'name': '银河沪深300价值指数',
    # 'ttype': 'fund', 'status': 'new', 'action': '022', 'amount': 317, 'status_desc': '交易进行中',
    # 'action_desc': '买入', 'created_at': 1629268603170, 'title': '银河沪深300价值指数',
    # 'value_desc': '317.00元', 'convert': False}
    return get_row(item.get('created_at'), item.get('action_desc'), item.get('code'), item.get('name'), amount,
                   price, share, service_fee, order_id)


def get_row(order_date, action_desc, code, name, amount, price, share, service_fee, order_id, parent_order_id=None):
    # one_day_second = 24 * 60 * 60
    # order_date_timestamp = math.floor(int(order_date) / (1000 * one_day_second)) * one_day_second
    row = [date_util.format_unix_datetime(date_util.DATE_FORMAT, order_date), action_desc, code, name, float(amount),
           float(price), float(share), float(service_fee), order_id,
           order_id if parent_order_id is None else parent_order_id]
    print(row)
    return row


def parse_swap_plan(parent_order):
    """解析组合
    {"data":{"order_id":"397120067162164224","uid":284893233,"code":"CSI666","name":"螺丝钉指数基金组合","ttype":"plan","status":"success","action":"036","percent":0,"volume":500,"target_code":"CSI666","target_name":"螺丝钉指数基金组合","status_desc":"交易成功","action_desc":"转换","created_at":1629268299807,"final_confirm_date":1629648000000,"total_fee":0.04,"title":"螺丝钉指数基金组合->螺丝钉指数基金组合","sub_order_list":[{"action_text":"成分基金转出信息","action":"038","orders":[{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"008127","fd_name":"广发趋势优选混合C","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"519671","target_fd_name":"银河沪深300价值指数","title":"广发趋势优选混合C","action_desc":"组合转出","status_desc":"交易成功","type":"plan","action":"038","status":"success","ts":1629216000000,"confirm_ts":1629302400000,"amount":0,"volume":6.84,"confirm_amount":11.16,"confirm_volume":6.84,"fee":0,"value_desc":"6.84份","value_text":"下单份额","confirm_value_text":"确认金额","confirm_value_desc":"11.16元","bank_name":"中国银行(4046)","order_id":"397120067287993344"},{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"008127","fd_name":"广发趋势优选混合C","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"519671","target_fd_name":"银河沪深300价值指数","title":"广发趋势优选混合C","action_desc":"组合转出","status_desc":"交易成功","type":"plan","action":"038","status":"success","ts":1629216000000,"confirm_ts":1629302400000,"amount":0,"volume":13.73,"confirm_amount":22.41,"confirm_volume":13.73,"fee":0,"value_desc":"13.73份","value_text":"下单份额","confirm_value_text":"确认金额","confirm_value_desc":"22.41元","bank_name":"招商银行(2565)","order_id":"397120067426405376"}]},{"action_text":"成分基金转入信息","action":"037","orders":[{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"519671","fd_name":"银河沪深300价值指数","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"008127","target_fd_name":"广发趋势优选混合C","title":"银河沪深300价值指数","action_desc":"组合转入","status_desc":"交易成功","type":"plan","action":"037","status":"success","ts":1629388800000,"confirm_ts":1629648000000,"amount":11.16,"volume":0,"confirm_amount":11.16,"confirm_volume":6.99,"fee":0.01,"value_desc":"11.16元","value_text":"下单金额","confirm_value_text":"确认份额","confirm_value_desc":"6.99份","bank_name":"中国银行(4046)","order_id":"397496351008694272"},{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"519671","fd_name":"银河沪深300价值指数","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"008127","target_fd_name":"广发趋势优选混合C","title":"银河沪深300价值指数","action_desc":"组合转入","status_desc":"交易成功","type":"plan","action":"037","status":"success","ts":1629388800000,"confirm_ts":1629648000000,"amount":22.41,"volume":0,"confirm_amount":22.41,"confirm_volume":14.02,"fee":0.03,"value_desc":"22.41元","value_text":"下单金额","confirm_value_text":"确认份额","confirm_value_desc":"14.02份","bank_name":"招商银行(2565)","order_id":"397496351025473536"}]}],"convert":true},"result_code":0}
    """
    parent_order_id = parent_order.get("order_id")
    order_dict = get_plan_order_detail(parent_order_id)
    rows = []
    for sub_orders in order_dict.get("data").get("sub_order_list"):
        for order in sub_orders.get("orders"):
            order_id = order.get("order_id")
            amount, share, price, service_fee = get_fund_buy_order_detail(order_id)
            row = get_row(order.get('ts'), parse_plan_action_name(order.get('action_desc')), order.get('fd_code'),
                          order.get('fd_name'), amount, price, share, service_fee, order_id, parent_order_id)
            rows.append(row)
    return rows


def parse_swap_plan_order_id(parent_order):
    """解析组合
    {"data":{"order_id":"397120067162164224","uid":284893233,"code":"CSI666","name":"螺丝钉指数基金组合","ttype":"plan","status":"success","action":"036","percent":0,"volume":500,"target_code":"CSI666","target_name":"螺丝钉指数基金组合","status_desc":"交易成功","action_desc":"转换","created_at":1629268299807,"final_confirm_date":1629648000000,"total_fee":0.04,"title":"螺丝钉指数基金组合->螺丝钉指数基金组合","sub_order_list":[{"action_text":"成分基金转出信息","action":"038","orders":[{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"008127","fd_name":"广发趋势优选混合C","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"519671","target_fd_name":"银河沪深300价值指数","title":"广发趋势优选混合C","action_desc":"组合转出","status_desc":"交易成功","type":"plan","action":"038","status":"success","ts":1629216000000,"confirm_ts":1629302400000,"amount":0,"volume":6.84,"confirm_amount":11.16,"confirm_volume":6.84,"fee":0,"value_desc":"6.84份","value_text":"下单份额","confirm_value_text":"确认金额","confirm_value_desc":"11.16元","bank_name":"中国银行(4046)","order_id":"397120067287993344"},{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"008127","fd_name":"广发趋势优选混合C","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"519671","target_fd_name":"银河沪深300价值指数","title":"广发趋势优选混合C","action_desc":"组合转出","status_desc":"交易成功","type":"plan","action":"038","status":"success","ts":1629216000000,"confirm_ts":1629302400000,"amount":0,"volume":13.73,"confirm_amount":22.41,"confirm_volume":13.73,"fee":0,"value_desc":"13.73份","value_text":"下单份额","confirm_value_text":"确认金额","confirm_value_desc":"22.41元","bank_name":"招商银行(2565)","order_id":"397120067426405376"}]},{"action_text":"成分基金转入信息","action":"037","orders":[{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"519671","fd_name":"银河沪深300价值指数","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"008127","target_fd_name":"广发趋势优选混合C","title":"银河沪深300价值指数","action_desc":"组合转入","status_desc":"交易成功","type":"plan","action":"037","status":"success","ts":1629388800000,"confirm_ts":1629648000000,"amount":11.16,"volume":0,"confirm_amount":11.16,"confirm_volume":6.99,"fee":0.01,"value_desc":"11.16元","value_text":"下单金额","confirm_value_text":"确认份额","confirm_value_desc":"6.99份","bank_name":"中国银行(4046)","order_id":"397496351008694272"},{"plan_code":"CSI666","plan_name":"螺丝钉指数基金组合","fd_code":"519671","fd_name":"银河沪深300价值指数","target_plan_code":"CSI666","target_plan_name":"螺丝钉指数基金组合","target_fd_code":"008127","target_fd_name":"广发趋势优选混合C","title":"银河沪深300价值指数","action_desc":"组合转入","status_desc":"交易成功","type":"plan","action":"037","status":"success","ts":1629388800000,"confirm_ts":1629648000000,"amount":22.41,"volume":0,"confirm_amount":22.41,"confirm_volume":14.02,"fee":0.03,"value_desc":"22.41元","value_text":"下单金额","confirm_value_text":"确认份额","confirm_value_desc":"14.02份","bank_name":"招商银行(2565)","order_id":"397496351025473536"}]}],"convert":true},"result_code":0}
    """
    order_dict = get_plan_order_detail(parent_order.get("order_id"))
    order_ids = []
    for sub_orders in order_dict.get("data").get("sub_order_list"):
        for order in sub_orders.get("orders"):
            order_ids.append(order.get("order_id"))
    return order_ids


def parse_plan_action_name(action_desc):
    return "卖出" if "组合转出" == action_desc else "买入" if "组合转入" == action_desc else action_desc


def get_plan_order_detail(order_id):
    """解析组合"""
    order_detail_resp = get(plan_order_detail.format(order_id))
    order_detail_text = order_detail_resp.text
    #     print(order_detail_text)
    return json.loads(order_detail_text)


def parse_trade(items, saved_order_id):
    rows = []
    for item in items:
        if "success" == item.get("status"):
            trade_type = item.get('ttype')
            action = item.get("action")
            if item.get("order_id") in saved_order_id:
                continue
            if DanjuanType.plan == trade_type:
                if DanjuanAction.swap == action or DanjuanAction.dividend == action or DanjuanAction.buy == action:
                    rows += parse_swap_plan(item)
                else:
                    print(f"trade_type={trade_type}, 不支持的交易类型{json.dumps(item)}")
            elif trade_type == DanjuanType.fund:
                try:
                    rows.append(parse_fund(item))
                except Exception as e:
                    print(f"trade_type={trade_type}, 不支持的交易类型{json.dumps(item)}", e)
            else:
                raise Exception(f"不支持的交易类型{json.dumps(item)}")
    return rows


def parse_trade_all(resp_dict):
    order_ids = [item.get("order_id") for item in resp_dict.get("data").get("items")] if resp_dict.get(
        "result_code") == 0 else []
    return order_ids
