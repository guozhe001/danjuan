# encoding=utf8

import logging
import os
import random
import uuid
from urllib.parse import urlencode

import requests
import requests.adapters

logger = logging.getLogger(__name__)

my_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Content-Type': 'application/json',
}

my_get_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
}

proxy_template = "http://%(user)s:%(pass)s@%(host)s:%(port)s"

# 代理服务器
proxyHost = "proxy.ipidea.io"
proxyPort = "2333"

# 代理隧道验证信息
proxyUser = "company-zone-custom"
proxyPass = "123456"

proxyMeta = proxy_template % {
    "host": proxyHost,
    "port": proxyPort,
    "user": proxyUser,
    "pass": proxyPass,
}

proxies = {
    "http": proxyMeta,
    "https": proxyMeta,
}


# http method相关
class HttpMethod:
    HTTP_METHOD_GET = "GET"
    HTTP_METHOD_POST = "POST"
    HTTP_METHOD_DELETE = "DELETE"


def get_with_headers(url, headers):
    return get_with_header_and_params(url, headers, None)


def get_with_header_and_params(url, headers, params):
    return request(url, HttpMethod.HTTP_METHOD_GET, headers, params, None)


def get_with_params(url, params):
    return get_with_header_and_params(url, my_get_headers, params)


def get(url):
    return get_with_headers(url, my_get_headers)


def post(url, data):
    return post_with_header(url, my_headers, {}, data)


def delete(url):
    return delete_with_params(url, {})


def delete_with_params(url, params):
    return delete_with_header_and_params(url, my_headers, params)


def delete_with_header_and_params(url, headers, params):
    return request(url, HttpMethod.HTTP_METHOD_DELETE, headers, params, {})


def post_with_params(url, params, data):
    return post_with_header(url, my_headers, params, data)


def post_with_header(url, headers, params, data):
    return request(url, HttpMethod.HTTP_METHOD_POST, headers, params, data)


def post_with_json(url, headers, params=None, data=None, json=None):
    return request_with_json(url, HttpMethod.HTTP_METHOD_POST, headers, params, data, json)


def request(url, method, headers, params, data):
    return request_with_json(url, method, headers, params, data, {})


def request_with_json(url, method, headers, params, data, json):
    request_id = str(uuid.uuid4())
    logger.debug(
        f"request_id={request_id}, url={url}, method={method},\n headers={headers},\n params={params}, \n data={data},"
        f" \n json={json}")
    response = requests.request(method=method, url=url, headers=headers, json=json, data=data, params=params,
                                )
    logger.debug("request_id={}, response={}".format(request_id, response.text))
    return response


def url_encode(params: dict) -> str:
    """
    将字典转换成url格式；注意如果某个参数的值是空，此参数也会出现在url中，需要自己过滤一下空value
    :param params:  参数字典
    :return:
    """
    return urlencode(params)


def curl(url):
    print(url)
    with os.popen(f'curl {url}') as web:
        return "".join(web.readlines())


def mogu_proxy_get(url):
    # 蘑菇代理的隧道订单
    appKey = "YTRSRlRMN3IzMUppU3AzdzpIN1BROUZPSFVRU096UmlW"

    # 蘑菇隧道代理服务器地址
    ip_port = 'secondtransfer.moguproxy.com:9001'

    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
    headers = {
        "Authorization": 'Basic ' + appKey
    }
    return requests.get(url, headers=headers, proxies=proxy, verify=False, allow_redirects=False)


#
# jiufang_proxy_ports = ["62667", "63143", "63349", "63856", "64682", "60041", "60606", "64840", "61099", "60610", "7419",
#                        "61050"]
# jiufang_proxy_ports = ["62667", "63143", "63349", "64682", "60041", "61099", "7419"]

jiufang_proxy_meta = proxy_template % {
    "host": "107.151.187.174",
    "port": "62667",
    "user": 'guozhe',
    "pass": "YfIFZPIUqe253215",
}

jiufang_proxies = {
    "http": jiufang_proxy_meta,
    "https": jiufang_proxy_meta,
}


def jiufang_proxy_get(url, headers=None):
    # 随机从不同国家选一个
    # port = jiufang_proxy_ports[random.randint(0, len(jiufang_proxy_ports) - 1)]
    return get_with_proxy(url, jiufang_proxies, headers)


def astoip_proxy_get(url):
    ip_list = ["209.205.212.34:1201", "209.205.212.34:1202", "209.205.212.34:1203", "209.205.212.34:1204",
               "209.205.212.34:1205", "209.205.212.34:1206", "209.205.212.34:1207", "209.205.212.34:1208",
               "209.205.212.34:1209", "209.205.212.34:1210", "209.205.212.34:1211", "209.205.212.34:1212",
               "209.205.212.34:1213", "209.205.212.34:1214", "209.205.212.34:1215", "209.205.212.34:1216",
               "209.205.212.34:1217", "209.205.212.34:1218", "209.205.212.34:1219", "209.205.212.34:1220"]
    user_name = "astoip255"
    password = "4b89d1-3a7c6d-82f4f8-39a784-13b86b"
    idx = random.randint(0, len(ip_list) - 1)
    astoip_proxy_meta = "http://%(user)s:%(pass)s@%(host)s" % {
        "host": ip_list[idx],
        "user": user_name,
        "pass": password,
    }
    astoip_proxies = {
        "http": astoip_proxy_meta,
        "https": astoip_proxy_meta,
    }
    return get_with_proxy(url, astoip_proxies)


def ipidea_proxy_get(url, headers=None):
    # 端口是2334, 使用2333有问题
    # ipidea_proxy_meta = "http://company-zone-custom:123456@proxy.ipidea.io:2334/"
    ipidea_proxy_meta = "http://fuze_com-zone-quark:fuze001@proxy.ipidea.io:2334/"
    ipidea_proxies = {
        "http": ipidea_proxy_meta,
        "https": ipidea_proxy_meta,
    }
    return get_with_proxy(url, ipidea_proxies, headers)


def get_with_proxy(url, proxy, headers=None):
    # logger.debug(proxy)
    # ip_resp = requests.get("http://icanhazip.com", proxies=proxy)
    # logger.info(f"proxy ip is: {ip_resp.text}")
    return requests.get(url, proxies=proxy, headers=headers if headers else my_get_headers, timeout=(5, 10))


def get_with_auth(url, oauth, is_stream=False, params=None):
    return requests.get(url, auth=oauth, stream=is_stream, params=params)


def post_with_auth(url, oauth, json=None):
    return requests.post(url, auth=oauth, json=json)


def get_with_short_url(url):
    """使用短链接请求"""
    s = requests.session()
    s.keep_alive = False
    resp = s.get(url=url)
    s.close()
    return resp
