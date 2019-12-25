from django.http import JsonResponse

class HttpCode:
    OK = 200
    PARAMS_ERROR =400
    UN_AUTH = 401
    METHOD_ERROR = 405
    SERVER_ERROR = 500

def result(code=HttpCode.OK, message='', data=None, **kwargs):
    json_dict = {
        'code': code,
        'message': message,
        'data': data
    }
    # kwargs不为None，是dict，有key
    if kwargs and isinstance(kwargs, dict) and kwargs.keys():
        json_dict.update(kwargs)

    return JsonResponse(json_dict)

def ok():
    return result()

def params_error(message='', data=None, **kwargs):
    return result(code=HttpCode.PARAMS_ERROR, message=message, data=data, **kwargs)

def auth_error(message='', data=None, **kwargs):
    return result(code=HttpCode.UN_AUTH, message=message, data=data, **kwargs)

def method_error(message='', data=None, **kwargs):
    return result(code=HttpCode.METHOD_ERROR, message=message, data=data, **kwargs)

def server_error(message='', data=None, **kwargs):
    return result(code=HttpCode.SERVER_ERROR, message=message, data=data, **kwargs)
