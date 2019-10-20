import api.fanyi as fanyi

api = {
    'fanyi': {
        'google': fanyi.google_fanyi_query,
        'tencent': fanyi.tencent_fanyi_query,
        'youdao': fanyi.youdao_fanyi_query,
        'baidu': fanyi.baidu_fanyi_query
    }
}


def api_call(action, param):
    if action == 'fanyi':
        vender = param['vender']
        return api[action][vender](param['q'], param['from'], param['to'])
