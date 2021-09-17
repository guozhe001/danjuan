import requests


def get(url, headers):
    resp = requests.get(url, headers=headers)
    return resp
