from collections import defaultdict
from django.db.models import Q
from django.utils import timezone as datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c
from ..core.views import ApproveViewSet, TMSViewSet
from ..core.permissions import IsDriverOrEscortUser
from . import models as m
from . import serializers as s
from ..finance.serializers import BillDocumentSerializer


class JobViewSet(TMSViewSet):
    """
    """
    queryset = m.Job.objects.all()
    serializer_class = s.JobSerializer
    data_view_serializer_class = s.JobDataViewSerializer

    def create(self, request):
        jobs = []

        # if vehicle & driver & escort is mulitple selected for delivers
        # we assume that this is one job
        for deliver in request.data:
            new_job = True
            order_id = deliver.get('order', None)
            driver_id = deliver.get('driver', None)
            escort_id = deliver.get('escort', None)
            vehicle_id = deliver.get('vehicle', None)
            deliver_id = deliver.get('mission', None)
            route_id = deliver.get('route', None)
            mission_weight = deliver.get('mission_weight', 0)

            for job in jobs:
                if (
                    job['driver'] == driver_id and
                    job['escort'] == escort_id and
                    job['vehicle'] == vehicle_id
                ):
                    job['mission_ids'].append(deliver_id)
                    job['mission_weights'].append(mission_weight)
                    job['total_weight'] += float(mission_weight)
                    new_job = False
                    continue

            if new_job:
                jobs.append({
                    'order': order_id,
                    'driver': driver_id,
                    'escort': escort_id,
                    'vehicle': vehicle_id,
                    'route': route_id,
                    'mission_ids': [deliver_id],
                    'mission_weights': [mission_weight],
                    'total_weight': float(mission_weight)
                })

        for job in jobs:
            context = {
                'mission_ids': job.pop('mission_ids', []),
                'mission_weights': job.pop('mission_weights', [])
            }

            serializer = self.serializer_class(
                data=job, context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            {'msg': 'Success'},
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=False, url_path='mileage'
    )
    def get_mileage(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all()
        )

        serializer = s.JobMileageSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='cost'
    )
    def get_cost(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all()
        )
        serializer = s.JobCostSerializer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='time'
    )
    def get_time(self, request):
        page = self.paginate_queryset(
            m.Job.objects.all(),
        )

        serializer = s.JobTimeSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @action(
        detail=False, url_path='driving'
    )
    def get_driving(self, request):
        pass

    @action(
        detail=False, url_path='previous',
        permission_classes=[IsDriverOrEscortUser]
    )
    def previous_jobs(self, request):
        serializer = s.JobDataViewSerializer(
            request.user.jobs_as_driver.filter(
                finished_on__lte=datetime.now()
            ),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path='done',
        permission_classes=[IsDriverOrEscortUser]
    )
    def done_jobs(self, request):
        serializer = s.JobDataViewSerializer(
            request.user.jobs_as_driver.completeds.all(),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path='current',
        permission_classes=[IsDriverOrEscortUser]
    )
    def progress_jobs(self, request):
        job = request.user.jobs_as_driver.filter(
            ~(Q(progress=c.JOB_PROGRESS_NOT_STARTED) |
                Q(progress=c.JOB_PROGRESS_COMPLETE))
        ).first()

        # if job is None:
        #     job = request.user.driver_profile.jobs.filter(
        #         progress=c.JOB_PROGRESS_NOT_STARTED
        #     ).first()

        if job is not None:
            ret = s.JobDataViewSerializer(job).data
        else:
            ret = {}

        return Response(
            ret,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path='future',
        permission_classes=[IsDriverOrEscortUser]
    )
    def future_jobs(self, request):
        serializer = s.JobDataViewSerializer(
            request.user.jobs_as_driver.filter(
                progress=c.JOB_PROGRESS_NOT_STARTED
            ),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, url_path='update-progress',
        permission_classes=[IsDriverOrEscortUser]
    )
    def progress_update(self, request, pk=None):
        job = self.get_object()

        progress = job.progress
        if progress == c.JOB_PROGRESS_COMPLETE:
            return Response(
                {'progress': 'This is already completed progress'},
                status=status.HTTP_200_OK
            )

        if job.route is None:
            return Response(
                {'route': 'Not found route in this job'},
                status=status.HTTP_404_NOT_FOUND
            )

        if progress == c.JOB_PROGRESS_NOT_STARTED:
            job.started_on = datetime.now()

        elif progress == c.JOB_PROGRESS_TO_LOADING_STATION:
            job.arrived_loading_station_on = datetime.now()

        elif progress == c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION:
            job.started_loading_on = datetime.now()

        elif progress == c.JOB_PROGRESS_LOADING_AT_LOADING_STATION:
            job.finished_loading_on = datetime.now()

        elif progress == c.JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION:
            job.departure_loading_station_on = datetime.now()

        elif progress == c.JOB_PROGRESS_TO_QUALITY_STATION:
            job.arrived_quality_station_on = datetime.now()

        elif progress == c.JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION:
            job.started_checking_on = datetime.now()

        elif progress == c.JOB_PROGRESS_CHECKING_AT_QUALITY_STATION:
            job.finished_checking_on = datetime.now()

        elif progress == c.JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION:
            job.departure_quality_station_on = datetime.now()

        elif (progress - c.JOB_PROGRESS_TO_UNLOADING_STATION) >= 0:
            us_progress = (progress - c.JOB_PROGRESS_TO_UNLOADING_STATION) % 4
            current_mission = job.mission_set.filter(
                is_completed=False
            ).first()
            if current_mission is not None:
                if us_progress == 0:
                    current_mission.arrived_station_on = datetime.now()

                elif us_progress == 1:
                    current_mission.started_unloading_on = datetime.now()

                elif us_progress == 2:
                    current_mission.finished_unloading_on = datetime.now()

                elif us_progress == 3:
                    current_mission.is_completed = True
                    current_mission.departure_station_on = datetime.now()
                    current_mission.save()

                    if not job.mission_set.filter(is_completed=False).exists():
                        job.progress = c.JOB_PROGRESS_COMPLETE
                        job.finished_on = datetime.now()
                        job.save()
                        return Response(
                            s.JobProgressSerializer(job).data,
                            status=status.HTTP_200_OK
                        )
        job.progress = progress + 1
        job.save()

        return Response(
            s.JobProgressSerializer(job).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, url_path='upload-bill-document', methods=['post'],
        permission_classes=[IsDriverOrEscortUser]
    )
    def upload_bill_document(self, request, pk=None):
        data = request.data
        data['job'] = pk
        serializer = BillDocumentSerializer(
            data=data,
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, url_path='bill-documents'
    )
    def bill_documents(self, request, pk=None):
        job = self.get_object()
        bills = job.bills.all()

        category = request.query_params.get('category', None)
        if category is not None:
            bills = job.bills.filter(category=category)

        bills_by_categories = defaultdict(lambda: defaultdict(list))

        for bill in bills:
            bills_by_categories[bill.category][bill.sub_category].append(bill)

        new_bills = []
        category_choices = dict((x, y) for x, y in c.BILL_CATEGORY)

        for category, group_by_category in bills_by_categories.items():
            bills_by_subcategories = []
            if category == c.BILL_FROM_LOADING_STATION:
                sub_categories = c.LOADING_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_QUALITY_STATION:
                sub_categories = c.QUALITY_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_UNLOADING_STATION:
                sub_categories = c.UNLOADING_STATION_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_OIL_STATION:
                sub_categories = c.OIL_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_TRAFFIC:
                sub_categories = c.TRAFFIC_BILL_SUB_CATEGORY
            elif category == c.BILL_FROM_OTHER:
                sub_categories = c.OTHER_BILL_SUB_CATEGORY
            sub_category_choices = dict((x, y) for x, y in sub_categories)

            for sub_category, group_by_sub_category in group_by_category.items():
                bills_by_subcategories.append({
                    'sub_category': {
                        'value': sub_category,
                        'text': sub_category_choices[sub_category]
                    },
                    'data': BillDocumentSerializer(
                        group_by_sub_category,
                        context={'request': request},
                        many=True
                    ).data
                })
            new_bills.append({
                'category': {
                    'value': category,
                    'text': category_choices[category]
                },
                'data': bills_by_subcategories
            })

        return Response(
            new_bills,
            status=status.HTTP_200_OK
        )


class MissionViewSet(viewsets.ModelViewSet):
    """
    """
    serializer_class = s.MissionSerializer

    def get_queryset(self):
        return m.Mission.objects.filter(
            job__id=self.kwargs['job_pk']
        )


class ParkingRequestViewSet(ApproveViewSet):

    queryset = m.ParkingRequest.objects.all()
    serializer_class = s.ParkingRequestSerializer
    data_view_serializer = s.ParkingRequestDataViewSerializer


class DriverChangeRequestViewSet(ApproveViewSet):

    queryset = m.DriverChangeRequest.objects.all()
    serializer_class = s.DriverChangeRequestSerializer
    data_view_serializer = s.DriverChangeRequestDataViewSerializer


class EscortChangeRequestViewSet(ApproveViewSet):

    queryset = m.EscortChangeRequest.objects.all()
    serializer_class = s.EscortChangeRequestSerializer
    data_view_serializer = s.EscortChangeRequestDataViewSerializer
