import random
import hashlib
import json
import time
import uuid

from urllib import request, parse


youdao_fanyi_api_base_url = 'https://openapi.youdao.com/api'
youdao_fanyi_app_key = '38c1b9b93c067479'
youdao_fanyi_secret_key = 'MNKnNIwuGC3LfOxrIYYzgYHk9aK2Ngfw'

q = '日本語'
salt = str(uuid.uuid1())
curtime = str(int(time.time()))
sign = youdao_fanyi_app_key + q + salt + curtime + youdao_fanyi_secret_key
sign = hashlib.sha256(sign.encode()).hexdigest()

form_data = {
    'q': q,
    'from': 'ja',
    'to': 'zh-CHS',
    'appKey': youdao_fanyi_app_key,
    'salt': salt,
    'sign': sign,
    'signType': 'v3',
    'curtime': curtime
}
data = parse.urlencode(form_data).encode('utf-8')
resp = request.urlopen(youdao_fanyi_api_base_url, data=data).read()
print(json.loads(resp))
