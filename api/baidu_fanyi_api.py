import random
import hashlib
import json

from urllib import request, parse

baidu_fanyi_api_base_url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
app_key = ''
secret_key = ''

q = '日本語'
salt = random.randint(32768, 65536)
sign = app_key + q + str(salt) + secret_key
sign = hashlib.md5(sign.encode()).hexdigest()

form_data = {
    'q': q,
    'from': 'jp',
    'to': 'zh',
    'appid': app_key,
    'salt': salt,
    'sign': sign
}
data = parse.urlencode(form_data).encode('utf-8')
resp = request.urlopen(baidu_fanyi_api_base_url, data=data).read()
print(json.loads(resp))
