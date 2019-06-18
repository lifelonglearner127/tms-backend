from . import models as m
from . import serializers as s
from ..core.views import ApproveViewSet, TMSViewSet


class RestRequestViewSet(ApproveViewSet):

    queryset = m.RestRequest.objects.all()
    serializer_class = s.RestRequestSerializer
    data_view_serializer_class = s.RestRequestDataViewSerializer


class DepartmentViewSet(TMSViewSet):

    queryset = m.Department.objects.all()
    serializer_class = s.DepartmentSerializer
    short_serializer_class = s.ShortDepartmentSerializer


class PositionViewSet(TMSViewSet):

    queryset = m.Position.objects.all()
    serializer_class = s.PositionSerializer
    short_serializer_class = s.ShortPositionSerializer


class RoleManagementViewSet(TMSViewSet):

    queryset = m.RoleManagement.objects.all()
    serializer_class = s.RoleManagementSerializer
    data_view_serializer_class = s.RoleManagementDataViewSerializer
