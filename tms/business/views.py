from django.utils import timezone
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

    def get_queryset(self):
        queryset = self.queryset
        request_type = self.request.query_params.get('type', None)
        if request_type == c.REQUEST_TYPE_REST:
            queryset = queryset.filter(request_type=c.REQUEST_TYPE_REST)

        if request_type == c.REQUEST_TYPE_VEHICLE_REPAIR:
            queryset = queryset.filter(request_type=c.REQUEST_TYPE_VEHICLE_REPAIR)

        return queryset

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
            'detail': request.data.pop('detail'),
            'request': request
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
            'detail': request.data.pop('detail'),
            'request': request
        }

        serializer = self.serializer_class(instance, data=request.data, context=context, partial=True)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='approve')
    def approve_request(self, request, pk=None):
        basic_request = self.get_object()
        if basic_request.approved is True:
            return Response(
                {
                    'msg': 'Already approved'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        elif basic_request.approved is False:
            return Response(
                {
                    'msg': 'Already declined'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        request_approver = basic_request.requestapprover_set.filter(approver=request.user).first()

        if request_approver is None:
            return Response(
                {
                    'msg': 'Cannot approve this request'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if basic_request.requestapprover_set.filter(step__lt=request_approver.step, approved=None).exists():
            return Response(
                {
                    'msg': 'You cannot approve this request until previous steps are approved'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        request_approver.approved = True
        request_approver.description = request.data.pop('description')
        request_approver.approved_time = timezone.now()
        request_approver.save()

        if not basic_request.requestapprover_set.filter(approved=False).exists():
            basic_request.approved = True
            basic_request.save()

        return Response(
            s.BasicRequestSerializer(basic_request).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='decline')
    def decline_request(self, request, pk=None):
        basic_request = self.get_object()

        if basic_request.approved is True:
            return Response(
                {
                    'msg': 'Already approved'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        elif basic_request.approved is False:
            return Response(
                {
                    'msg': 'Already declined'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        request_approver = basic_request.requestapprover_set.filter(approver=request.user).first()

        if request_approver is None:
            return Response(
                {
                    'msg': 'Cannot decline this request'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if basic_request.requestapprover_set.filter(step__lt=request_approver.step, approved=None).exists():
            return Response(
                {
                    'msg': 'You cannot decline this request until previous steps are approved'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        request_approver.approved = False
        request_approver.description = request.data.pop('description')
        request_approver.approved_time = timezone.now()
        request_approver.save()

        basic_request.approved = False
        basic_request.save()

        return Response(
            s.BasicRequestSerializer(basic_request).data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, url_path='cancel')
    def cancel_my_request(self, request, pk=None):
        basic_request = self.get_object()
        if basic_request.requester != request.user:
            return Response(
                {
                    'msg': 'Cannot cancel the request'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        basic_request.is_cancelled = True
        basic_request.cancelled_time = timezone.now()
        basic_request.save()
        return Response(
            {
                'msg': 'Successfully cancelled'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="unapproved-requests")
    def get_unapproved_requests(self, request):
        return Response(
            s.BasicRequestSerializer(
                m.BasicRequest.unapproved_requests.all(),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="get-my-manageable-requests")
    def get_my_manageable_requests(self, request):
        return Response(
            s.BasicRequestSerializer(
                m.BasicRequest.objects.filter(approvers=request.user),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="get-my-manageable-approved-requests")
    def get_my_manageable_approved_requests(self, request):
        return Response(
            s.BasicRequestSerializer(
                m.BasicRequest.objects.filter(approvers=request.user, approved=True),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="get-my-manageable-declined-requests")
    def get_my_manageable_declined_requests(self, request):
        return Response(
            s.BasicRequestSerializer(
                m.BasicRequest.objects.filter(approvers=request.user, approved=False),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="get-my-manageable-waiting-requests")
    def get_my_manageable_waiting_requests(self, request):
        return Response(
            s.BasicRequestSerializer(
                m.BasicRequest.objects.filter(approvers=request.user, approved=None),
                many=True,
                context={'request': request}
            ).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path="me")
    def get_my_requests(self, request):
        """
        Get my request; used in driver app
        """
        page = self.paginate_queryset(
            request.user.my_requests.all()
        )
        serializer = s.BasicRequestSerializer(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/approved")
    def get_my_approved_requests(self, request):
        """
        Get my approved request; used in driver app
        """
        page = self.paginate_queryset(
            request.user.my_requests.filter(approved=True)
        )
        serializer = s.BasicRequestSerializer(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/unapproved")
    def get_my_unapproved_request(self, request):
        """
        Get my unapproved request; used in driver app
        """
        page = self.paginate_queryset(
            request.user.my_requests.filter(approved=False)
        )
        serializer = s.BasicRequestSerializer(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="me/ccs")
    def get_my_cc_request(self, request):
        """
        Get the request that I was chosen as cc; used in driver app
        """
        page = self.paginate_queryset(
            m.BasicRequest.objects.filter(ccs__id=request.user.id)
        )
        serializer = s.BasicRequestSerializer(
            page,
            context={
                'request': request
            },
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="rest-request/categories")
    def get_rest_request_categories(self, request):
        page = self.paginate_queryset(
            [{'value': x, 'text': y} for (x, y) in c.REST_REQUEST_CATEGORY]
        )
        serializer = ChoiceSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, url_path="vehicle-request/categories")
    def get_vehicle_repaire_request_categories(self, request):
        page = self.paginate_queryset(
            [{'value': x, 'text': y} for (x, y) in c.VEHICLE_REPAIR_REQUEST_CATEGORY]
        )
        serializer = ChoiceSerializer(page, many=True)
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
