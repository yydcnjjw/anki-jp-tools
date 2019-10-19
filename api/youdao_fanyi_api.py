import random
import hashlib
import json
import time
import uuid

from urllib import request, parse


youdao_fanyi_api_base_url = 'https://openapi.youdao.com/api'
app_key = ''
secret_key = ''

q = '日本語'
salt = str(uuid.uuid1())
curtime = str(int(time.time()))
sign = app_key + q + salt + curtime + secret_key
sign = hashlib.sha256(sign.encode()).hexdigest()

form_data = {
    'q': q,
    'from': 'ja',
    'to': 'zh-CHS',
    'appKey': app_key,
    'salt': salt,
    'sign': sign,
    'signType': 'v3',
    'curtime': curtime
}
data = parse.urlencode(form_data).encode('utf-8')
resp = request.urlopen(youdao_fanyi_api_base_url, data=data).read()
print(json.loads(resp))
