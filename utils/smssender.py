#encoding: utf-8

import requests

def send(mobile,captcha):
    url = "http://v.juhe.cn/sms/send"
    params = {
        "mobile": mobile,
        "tpl_id": "121674",
        "tpl_value": "#code#="+captcha,
        "key": "4f2dc49ce16b8538522f0f11fb6cd0a2"
    }
    response = requests.get(url,params=params)
    result = response.json()
    if result['error_code'] == 0:
        return True
    else:
        return False
