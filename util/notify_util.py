# -*- coding: utf8 -*-

import logging

from util import http_util

logger = logging.getLogger(__name__)

notify_section = "notify"
notify_open_key = "open"
notify_url_key = "url"

title = "投资理财通知"

# 设置在一段时间内不重复通知；120秒内不重复通知
NOTIFY_INTERVAL_TIME = 120

notify_message_temp = """\n交易所为：{}\n上币公告：{}\n发布时间：{}\n公告url：{}\n"""

url = "https://sctapi.ftqq.com/SCT15083TCG0UuSatcAIiWj01ztylMk46.send"


def notify_with_platform(message, _title=title):
    """
    指定平台通知
    :param message:  通知内容
    :param _title:   通知名称
    :return:
    """
    params = {"title": _title, "desp": message}
    logger.info(f"notify url={url}, params={params}")
    r = http_util.post_with_json(url, http_util.my_headers, params=params, json=params)
    logger.info(r.text.encode('utf8').decode('unicode_escape'))
    logger.info(f"notify response={r.text}")