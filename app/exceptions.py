class JRError(Exception):
    code = -1
    msg = '未知错误'

    @property
    def ret(self):
        return {'code': self.code, 'msg': self.msg}

    def __init__(self, *args, c_msg=None, **kwargs):
        if c_msg is not None:
            self.msg = c_msg
        return super().__init__(*args, **kwargs)


class WXError(JRError):
    code = -9
    msg = '微信登陆失败'


class RequestError(JRError):
    code = -4
    msg = '服务器未知请求错误'


class RequestDateError(RequestError):
    code = -5
    msg = '服务器获取数据失败'


class RequestFormatError(RequestError):
    code = -6
    msg = '服务器解析数据失败'


class RequestTimeoutError(RequestError):
    code = -3
    msg = '服务器http请求超时'


class CodeNoneError(WXError):
    code = -2
    msg = '微信认证代码为空'


class ParameterError(JRError):
    code = -7
    msg = 'API 参数错误'


class FindError(JRError):
    code = -8
    msg = '未找到相应的书籍'


class NeedLoginError(JRError):
    code = -10
    msg = '需要登陆'
