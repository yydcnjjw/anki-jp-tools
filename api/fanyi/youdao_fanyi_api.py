import random
import hashlib
import json
import time
import uuid

from urllib import request, parse

from conf import get_conf

__youdao_fanyi_api_base_url = 'https://openapi.youdao.com/api'
__youdao_conf = get_conf('youdao')


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def youdao_fanyi_query(q, f, t):
    if __youdao_conf is None:
        return

    app_key = __youdao_conf['fanyi_app_key']
    secret_key = __youdao_conf['fanyi_secret_key']

    salt = str(uuid.uuid1())
    curtime = str(int(time.time()))
    sign = app_key + truncate(q) + salt + curtime + secret_key
    sign = hashlib.sha256(sign.encode('utf-8')).hexdigest()

    form_data = {
        'q': q,
        'from': f,
        'to': t,
        'appKey': app_key,
        'salt': salt,
        'sign': sign,
        'signType': 'v3',
        'curtime': curtime
    }

    data = parse.urlencode(form_data).encode('utf-8')
    resp = json.loads(request.urlopen(
        __youdao_fanyi_api_base_url, data=data).read().decode('utf-8'))

    if resp['errorCode'] != '0':
        raise Exception(resp['errorCode'])
    return resp['translation']
