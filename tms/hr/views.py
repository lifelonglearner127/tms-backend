from . import models as m
from . import serializers as s
from ..core.views import ApproveViewSet


class RestRequestViewSet(ApproveViewSet):

    queryset = m.RestRequest.objects.all()
    serializer_class = s.RestRequestSerializer
    data_view_serializer_class = s.RestRequestDataViewSerializer
