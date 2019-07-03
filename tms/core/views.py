from django.utils import timezone as datetime

from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from .permissions import IsStaffUser


class TMSViewSet(viewsets.ModelViewSet):
    """
    Vieweset only allowed for admin or staff permission
    """
    short_serializer_class = None
    data_view_serializer_class = None

    def get_serializer_class(self):
        if self.action not in ['create', 'update'] and\
           self.data_view_serializer_class is not None:
            return self.data_view_serializer_class
        else:
            return self.serializer_class

    def get_short_serializer_class(self):
        if self.short_serializer_class is not None:
            return self.short_serializer_class

        return self.serializer_class

    @action(detail=False)
    def short(self, request):
        serializer = self.get_short_serializer_class()(
            self.get_queryset(),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class StaffViewSet(TMSViewSet):
    """
    Vieweset only allowed for admin or staff permission
    """
    permission_classes = [IsStaffUser]


class ApproveViewSet(TMSViewSet):

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        approved = request.data.get('approve', False)
        instance = self.get_object()
        instance.approved = approved
        instance.approved_time = datetime.now()
        instance.save()

        serializer = self.get_serializer_class()(instance)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='approved-requests')
    def approved_requests(self, request):
        serializer = self.get_serializer_class()(
            self.get_queryset().filter(approved=True),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='unapproved-requests')
    def unapproved_requests(self, request):
        serializer = self.get_serializer_class()(
            self.get_queryset().filter(approved=False),
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class StaffAPIView(APIView):
    """
    APIView only allowed for admin or staff permission
    """
    permission_classes = [IsStaffUser]


class ShortAPIView(StaffAPIView):
    """
    View to list short data of specified model
    """
    model_class = None
    serializer_class = None

    def get_queryset(self):
        return self.model_class.objects.all()

    def get(self, request):
        serializer = self.serializer_class(
            self.get_queryset(),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
