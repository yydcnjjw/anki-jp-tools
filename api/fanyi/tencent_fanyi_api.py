import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models


from conf import get_conf
__tencent_conf = get_conf('tencent')


def tencent_fanyi_query(q, f, t):
    if __tencent_conf is None:
        return
    app_key = __tencent_conf['fanyi_app_key']
    secret_key = __tencent_conf['fanyi_secret_key']
    try:
        cred = credential.Credential(
            app_key, secret_key)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "tmt.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = tmt_client.TmtClient(cred, "ap-shanghai", clientProfile)

        req = models.TextTranslateRequest()

        params = json.dumps({
            'SourceText': q,
            'Source': f,
            'Target': t,
            'ProjectId': '1129592'
        }).encode('utf-8')
        req.from_json_string(params)

        resp = client.TextTranslate(req)
        return [resp.TargetText]

    except TencentCloudSDKException as err:
        print(err)
