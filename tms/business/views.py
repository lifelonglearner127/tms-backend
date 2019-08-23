from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

# constants
from ..core import constants as c

# models
from . import models as m

# serializers
from . import serializers as s
from ..core.serializers import ChoiceSerializer

# views
from ..core.views import TMSViewSet


# class ParkingRequestViewSet(TMSViewSet):

#     queryset = m.ParkingRequest.objects.all()
#     serializer_class = s.ParkingRequestSerializer
#     data_view_serializer = s.ParkingRequestDataViewSerializer

#     def create(self, request):
#         data = request.data
#         data['driver'] = request.user.id
#         serializer = self.serializer_class(
#             data=data
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )

#     def update(self, request, pk=None):
#         instance = self.get_object()
#         data = request.data
#         data['driver'] = request.user.id
#         serializer = self.serializer_class(
#             instance, data=data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


# class DriverChangeRequestViewSet(TMSViewSet):

#     queryset = m.DriverChangeRequest.objects.all()
#     serializer_class = s.DriverChangeRequestSerializer

#     def create(self, request):
#         data = request.data
#         data['old_driver'] = request.user.id
#         serializer = self.serializer_class(
#             data=data
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )

#     def update(self, request, pk=None):
#         instance = self.get_object()
#         data = request.data
#         data['old_driver'] = request.user.id
#         if data['new_driver'] == data['old_driver']:
#             raise s.serializers.ValidationError({
#                 'new_driver': 'Cannot set the same driver'
#             })

#         serializer = self.serializer_class(
#             instance, data=data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


# class EscortChangeRequestViewSet(TMSViewSet):

#     queryset = m.EscortChangeRequest.objects.all()
#     serializer_class = s.EscortChangeRequestSerializer
#     data_view_serializer = s.EscortChangeRequestDataViewSerializer

#     def create(self, request):
#         data = request.data
#         data['old_escort'] = request.user.id
#         serializer = self.serializer_class(
#             data=data
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )

#     def update(self, request, pk=None):
#         instance = self.get_object()
#         data = request.data
#         data['old_escort'] = request.user.id
#         if data['new_escort'] == data['old_escort']:
#             raise s.serializers.ValidationError({
#                 'new_escort': 'Cannot set the same escort'
#             })

#         serializer = self.serializer_class(
#             instance, data=data, partial=True
#         )
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(
#             serializer.data,
#             status=status.HTTP_200_OK
#         )


class BasicRequestViewSet(TMSViewSet):
    queryset = m.BasicRequest.objects.all()
    serializer_class = s.BasicRequestSerializer

    def create(self, request):
        requester = request.data.pop('requester', None)
        if requester is not None:
            requester = get_object_or_404(m.User, id=requester.get('id', None))
        else:
            requester = request.user

        context = {
            'requester': requester,
            'approvers': request.data.pop('approvers', []),
            'ccs': request.data.pop('ccs', []),
            'images': request.data.pop('images', []),
            'detail': request.data.pop('detail')
        }

        serializer = self.serializer_class(data=request.data, context=context)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        for approver in instance.requestapprover_set.all():
            if approver.approved:
                return Response({
                    'msg': 'You can not update your request because it is in under approve flow'
                })

        requester = request.data.pop('requester', None)
        if requester is not None:
            requester = get_object_or_404(m.User, id=requester.get('id', None))
        else:
            requester = request.user

        context = {
            'requester': requester,
            'approvers': request.data.pop('approvers', []),
            'ccs': request.data.pop('ccs', []),
            'detail': request.data.pop('detail')
        }

        serializer = self.serializer_class(instance, data=request.data, context=context, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="me")
    def get_my_requests(self, request):
        page = self.paginate_queryset(
            request.user.my_requests.all()
        )
        serializer = s.BasicRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/approved")
    def get_my_approved_requests(self, request):
        page = self.paginate_queryset(
            request.user.my_requests.filter(approved=True)
        )
        serializer = s.BasicRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/unapproved")
    def get_my_unapproved_request(self, request):
        page = self.paginate_queryset(
            request.user.my_requests.filter(approved=False)
        )
        serializer = s.BasicRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/ccs")
    def get_my_cc_request(self, request):
        page = self.paginate_queryset(
            m.BasicRequest.objects.filter(ccs__id=request.user.id)
        )
        serializer = s.BasicRequestSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class RestRequestCateogryAPIView(APIView):

    def get(self, request):
        serializer = ChoiceSerializer(
            [
                {'value': x, 'text': y} for (x, y) in c.REST_REQUEST_CATEGORY
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class VehicleRepairRequestCategoryAPIView(APIView):

    def get(self, request):
        serializer = ChoiceSerializer(
            [
                {'value': x, 'text': y} for (x, y) in c.VEHICLE_REPAIR_REQUEST_CATEGORY
            ],
            many=True
        )
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
