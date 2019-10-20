from conf import get_conf
import random
import hashlib
import json

from urllib import request, parse


__baidu_fanyi_api_base_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
__baidu_conf = get_conf('baidu')


def baidu_fanyi_query(q, f, t):
    if __baidu_conf is None:
        return
    app_key = __baidu_conf['fanyi_app_key']
    secret_key = __baidu_conf['fanyi_secret_key']

    salt = random.randint(32768, 65536)
    sign = app_key + q + str(salt) + secret_key
    sign = hashlib.md5(sign.encode()).hexdigest()

    form_data = {
        'q': q,
        'from': f,
        'to': t,
        'appid': app_key,
        'salt': salt,
        'sign': sign
    }

    data = parse.urlencode(form_data).encode('utf-8')
    resp = json.loads(request.urlopen(
        __baidu_fanyi_api_base_url, data=data).read().decode('utf-8'))

    return list(map(lambda r: r['dst'], resp['trans_result']))
