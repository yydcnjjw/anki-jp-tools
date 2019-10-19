import json

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.tmt.v20180321 import tmt_client, models

app_key = ''
app_secret = ''

try:
    cred = credential.Credential(
        app_key, app_secret)
    httpProfile = HttpProfile()
    httpProfile.endpoint = "tmt.tencentcloudapi.com"

    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    client = tmt_client.TmtClient(cred, "ap-shanghai", clientProfile)

    req = models.TextTranslateRequest()

    text = '日本語'
    params = json.dumps({
        'SourceText': text,
        'Source': 'jp',
        'Target': 'zh',
        'ProjectId': '1129592'
    }).encode('utf-8')
    req.from_json_string(params)

    resp = client.TextTranslate(req)
    print(resp.to_json_string())

except TencentCloudSDKException as err:
    print(err)
