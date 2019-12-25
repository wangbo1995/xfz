from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
import json

ACCESS_KEY_ID = "LTAI4Fqc4NTcE1Qcy1iK8oNc"
ACCESS_KEY_SECRET = "9Uus7WHRFThKq4bfvcaHXBsMKxRsvn"
client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, 'cn-hangzhou')

request = CommonRequest()
request.set_accept_format('json')
request.set_domain('dysmsapi.aliyuncs.com')
request.set_method('POST')
request.set_protocol_type('https') # https | http
request.set_version('2017-05-25')
request.set_action_name('SendSms')

def send_sms(phone_numbers, code):
    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phone_numbers)
    request.add_query_param('SignName', "Python个人社区")
    request.add_query_param('TemplateCode', "SMS_180055687")
    # 第二个参数需要是JSON字符串
    request.add_query_param('TemplateParam', json.dumps({'code': code}))

    response = client.do_action(request)
    print(str(response, encoding='utf-8'))
    return response
