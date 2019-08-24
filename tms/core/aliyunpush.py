from aliyunsdkpush.request.v20160801 import PushRequest
from aliyunsdkcore import client
from django.conf import settings


aliyun_client = client.AcsClient(
    settings.ALIYUN_ACCESS_KEY_ID,
    settings.ALIYUN_ACCESS_KEY_SECRET,
    'cn-hangzhou'
)
aliyun_request = PushRequest.PushRequest()
aliyun_request.set_AppKey(settings.ALIYUN_MOBILE_PUSH_APP_KEY)
aliyun_request.set_Target('ALL')
aliyun_request.set_DeviceType('ANDROID')
aliyun_request.set_PushType('NOTICE')
