import json
import re
import math

from urllib import request, parse

from conf import get_conf, put_conf
__google_conf = get_conf('google')

__google_fanyi_api_base_url = 'https://translate.google.cn/translate_a/single'
__google_fanyi_home_page_url = 'https://translate.google.cn'

__google_access_header = {
    'user-agent': 'user-agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36'
}


def get_tkk():
    req = request.Request(__google_fanyi_home_page_url,
                          headers=__google_access_header)
    resp = request.urlopen(req).read().decode('utf-8')
    tkk_match = re.search(r'tkk:\'(\d*).(\d*)\'', resp)
    tkk_pair = (tkk_match.group(1), tkk_match.group(2))
    return '{}.{}'.format(tkk_pair[0], tkk_pair[1])


def rshift(val, n):
    """python port for '>>>'(right shift with padding)
    """
    return (val % 0x100000000) >> n


def __xr(a, b):
    size_b = len(b)
    c = 0
    while c < size_b - 2:
        d = b[c + 2]
        d = ord(d[0]) - 87 if 'a' <= d else int(d)
        d = rshift(a, d) if '+' == b[c + 1] else a << d
        a = a + d & 4294967295 if '+' == b[c] else a ^ d

        c += 3
    return a


def get_tk(text, tkk):
    a = []
    # Convert text to ints
    for i in text:
        val = ord(i)
        if val < 0x10000:
            a += [val]
        else:
            # Python doesn't natively use Unicode surrogates, so account for those
            a += [
                math.floor((val - 0x10000)/0x400 + 0xD800),
                math.floor((val - 0x10000) % 0x400 + 0xDC00)
            ]

    b = tkk if tkk != '0' else ''
    d = b.split('.')
    b = int(d[0]) if len(d) > 1 else 0

    # assume e means char code array
    e = []
    g = 0
    size = len(text)
    while g < size:
        l = a[g]
        # just append if l is less than 128(ascii: DEL)
        if l < 128:
            e.append(l)
        # append calculated value if l is less than 2048
        else:
            if l < 2048:
                e.append(l >> 6 | 192)
            else:
                # append calculated value if l matches special condition
                if (l & 64512) == 55296 and g + 1 < size and \
                        a[g + 1] & 64512 == 56320:
                    g += 1
                    # This bracket is important
                    l = 65536 + ((l & 1023) << 10) + (a[g] & 1023)
                    e.append(l >> 18 | 240)
                    e.append(l >> 12 & 63 | 128)
                else:
                    e.append(l >> 12 | 224)
                e.append(l >> 6 & 63 | 128)
            e.append(l & 63 | 128)
        g += 1
    a = b
    for i, value in enumerate(e):
        a += value
        a = __xr(a, '+-a^+6')
    a = __xr(a, '+-3^+b+-f')
    a ^= int(d[1]) if len(d) > 1 else 0
    if a < 0:  # pragma: nocover
        a = (a & 2147483647) + 2147483648
    a %= 1000000  # int(1E6)

    return '{}.{}'.format(a, a ^ b)


def google_fanyi_query(q, f, t):
    global __google_conf
    if __google_conf is None:
        __google_conf = {
            'ttk': get_tkk()
        }
        put_conf('google', __google_conf)

    tkk = __google_conf['ttk']
    tk = get_tk(q, tkk)
    form_data = [
        ('client', 'webapp'),
        ('sl', f),
        ('tl', t),
        ('hl', 'zh-CN'),
        ('dt', 'at'),
        ('dt', 'bd'),
        ('dt', 'ex'),
        ('dt', 'ld'),
        ('dt', 'md'),
        ('dt', 'qca'),
        ('dt', 'rw'),
        ('dt', 'rm'),
        ('dt', 'ss'),
        ('dt', 't'),
        ('tk', tk),
        ('q', q)
    ]
    data = parse.urlencode(form_data).encode('utf-8')
    resp = request.urlopen(__google_fanyi_api_base_url,
                           data=data).read().decode('utf-8')

    return list(filter(lambda x: x is not None, map(lambda x: x[0], json.loads(resp)[0])))
