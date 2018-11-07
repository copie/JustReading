import json
import logging
from functools import wraps
from json import JSONDecodeError
from traceback import format_exc

from flask import current_app, jsonify
from flask_login import current_user
from jsoncomment import JsonComment
from requests import request
from requests.exceptions import RequestException, Timeout

from app.exceptions import (JRError, NeedLoginError, RequestError,
                            RequestFormatError, RequestTimeoutError, WXError)

parser = JsonComment(json)

log = logging.getLogger(__name__)


def check_return(need_login=True):
    def wraps_(func):
        @wraps(func)
        def wraps__(*args, **kwargs):
            try:
                if need_login and not current_user.is_authenticated:
                    raise NeedLoginError
                ret = func(*args, **kwargs) or {}
                assert isinstance(ret, dict)
            except JRError as e:
                log.error(format_exc())
                ret = e.ret
            except Exception:
                log.error(format_exc())
                ret = {'code': -1, 'msg': '未知错误'}
            if 'code' not in ret:
                ret.update({'code': 0, 'msg': "请求成功"})
            return jsonify(ret)
        return wraps__
    return wraps_


def http_get(url, payload=None):
    if payload is None:
        payload = {}
    try:
        ret = request('GET', url, params=payload, timeout=10)
        if ret.status_code != 200:
            raise RequestDateError
        text = ret.content.decode(errors='ignore').strip().strip('\ufeff')
        ret = parser.loads(text)
    except Timeout:
        raise RequestTimeoutError
    except RequestException:
        raise RequestError
    return ret


def format_in_site_search_data(datas, page, count=20):
    def get_img_url(url_str):
        return url_str
    ret = {}
    items = ret['items'] = []
    try:
        for data in datas['data']:
            item = {}
            item['Name'] = data['Name']
            item['Author'] = data['Author']
            item['Img'] = get_img_url(data['Img'])
            item['Desc'] = data['Desc']
            items.append(item)
    except Exception:
        raise RequestFormatError

    ret['pageSize'] = len(items)
    ret['pageNo'] = page
    return ret


def format_easo_search_data(datas, page, count=20):
    def get_img_url(url_str):
        return url_str
    ret = {}
    items = ret['items'] = []
    try:
        for data in datas['all_book_items']:
            item = {}
            item['Name'] = data['name']
            item['Author'] = data['author']
            item['Img'] = get_img_url(data['imgUrl'])
            item['Desc'] = data['desc']
            items.append(item)
    except Exception:
        raise RequestFormatError

    ret['pageSize'] = len(items)
    ret['pageNo'] = page
    return ret


def format_zhuishu_search_data(datas, page, count=20):
    def get_img_url(url_str):
        return 'http://statics.zhuishushenqi.com/' + url_str
    ret = {}
    items = ret['items'] = []
    try:
        for data in datas['books'][(page-1)*count:page*count]:
            item = {}
            item['Name'] = data['title']
            item['Author'] = data['author']
            item['Img'] = get_img_url(data['cover'])
            item['Desc'] = data['shortIntro']
            items.append(item)
    except Exception:
        raise RequestFormatError

    ret['pageSize'] = len(items)
    ret['pageNo'] = page
    return ret


def in_site_search(key, page, count=20, siteid='app'):
    url = 'https://sou.jiaston.com/search.aspx'
    payload = {
        'key': key,
        'page': page,
        'siteid': siteid
    }
    ret = http_get(url, payload)
    return format_in_site_search_data(ret, page, count)


def easo_search(word, page, count=20, cid='eef_', os='ios', appverion='1049'):
    url = 'http://api.easou.com/api/bookapp/searchdzh.m'
    payload = {
        'word': word,
        'page_id': page,
        'count': count,
        'cid': cid,
        'os': os,
        'appverion': appverion
    }
    ret = http_get(url, payload)
    return format_easo_search_data(ret, page, count)


def zhuishu_search(query, page, count=20):
    url = 'http://api02u58f.zhuishushenqi.com/book/fuzzy-search'
    payload = {
        'query': query
    }
    ret = http_get(url, payload)
    return format_zhuishu_search_data(ret, page, count)


def code2openid(code):
    url = 'https://api.weixin.qq.com/sns/jscode2session'
    appid = current_app.config.get('APPID')
    secret = current_app.config.get('APPSECRET')
    data = {
        'appid': appid,
        'secret': secret,
        'js_code': code,
        'grant_type': 'authorization_code'
    }
    data = http_get(url, data)
    if 'openid' not in data:
        raise WXError(c_msg=data['errmsg'])
    return data['openid']


def get_book_info(bookid):
    url = 'http://quapp.1122dh.com/info/{bookid}.html'.format(bookid=bookid)

    data = http_get(url)
    ret = {}
    try:
        data = data['data']
        ret['data'] = data
    except Exception:
        raise RequestFormatError
    return ret
