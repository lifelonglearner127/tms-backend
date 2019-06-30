from django.db.models import Q
from django.utils import timezone as datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

# constants
from ..core import constants as c

# permissions
from ..core.permissions import IsDriverOrEscortUser

# models
from . import models as m

# serializers
from . import serializers as s

# views
from ..core.views import TMSViewSet


class OrderViewSet(TMSViewSet):
    """
    Order Viewset
    """
    queryset = m.Order.objects.all()
    serializer_class = s.OrderSerializer
    # data_view_serializer_class = s.OrderDataViewSerializer

    def create(self, request):
        context = {
            'loading_stations': request.data.pop('loading_stations'),
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer')
        }

        serializer = s.OrderSerializer(
            data=request.data, context=context
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        serializer_instance = self.get_object()

        context = {
            'loading_stations': request.data.pop('loading_stations'),
            'assignee': request.data.pop('assignee'),
            'customer': request.data.pop('customer')
        }

        serializer = s.OrderSerializer(
            serializer_instance,
            data=request.data,
            context=context,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def list(self, request):
        page = self.paginate_queryset(
            self.get_queryset().all()
        )

        serializer = s.OrderDataViewSerializer(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

    # @action(detail=True, url_path='jobs')
    # def get_jobs(self, request, pk=None):
    #     order = self.get_object()
    #     serializer = ShortJobSerializer(
    #         order.jobs.all(),
    #         many=True
    #     )

    #     return Response(
    #         serializer.data,
    #         status=status.HTTP_200_OK
    #     )

    @action(detail=True, methods=['post'], url_path='jobs')
    def create_job(self, request, pk=None):
        order = self.get_object()

        jobs = []

        # if vehicle & driver & escort is mulitple selected for delivers
        # we assume that this is one job
        for deliver in request.data:
            new_job = True
            order_id = order.id

            driver_data = deliver.get('driver', None)
            driver_id = driver_data.get('id', None)

            escort_data = deliver.get('escort', None)
            escort_id = escort_data.get('id', None)

            vehicle_data = deliver.get('vehicle', None)
            vehicle_id = vehicle_data.get('id', None)

            route_data = deliver.get('route', None)
            route_id = route_data.get('id', None)

            deliver_id = deliver.get('mission', None)
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

            serializer = s.JobSerializer(
                data=job, context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(
            {'msg': 'Success'},
            status=status.HTTP_201_CREATED
        )


class OrderLoadingStationViewSet(viewsets.ModelViewSet):
    """
    OrderProduct Viewset
    """
    serializer_class = s.OrderLoadingStationSerializer

    def get_queryset(self):
        return m.OrderLoadingStation.objects.filter(
            order__id=self.kwargs['order_pk']
        )


class OrderProductViewSet(viewsets.ModelViewSet):
    """
    OrderProduct Viewset
    """
    serializer_class = s.OrderProductSerializer

    def get_queryset(self):
        return m.OrderProduct.objects.filter(
            order_loading_station__id=self.kwargs['orderloadingstation_pk']
        )


class OrderProductDeliverViewSet(viewsets.ModelViewSet):
    """
    OrderProductDeliver ViewSet
    """
    serializer_class = s.OrderProductDeliverSerializer

    def get_queryset(self):
        return m.OrderProductDeliver.objects.filter(
            order_product__id=self.kwargs['orderproduct_pk']
        )


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
            order_data = deliver.get('order', None)
            order_id = order_data.get('id', None)

            driver_data = deliver.get('driver', None)
            driver_id = driver_data.get('id', None)

            escort_data = deliver.get('escort', None)
            escort_id = escort_data.get('id', None)

            vehicle_data = deliver.get('vehicle', None)
            vehicle_id = vehicle_data.get('id', None)

            route_data = deliver.get('route', None)
            route_id = route_data.get('id', None)

            deliver_id = deliver.get('mission', None)
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
        page = self.paginate_queryset(
            request.user.jobs_as_driver.filter(
                progress=c.JOB_PROGRESS_COMPLETE
            ).order_by('-finished_on')
        )

        serializer = s.JobDoneSerializer(
            page,
            many=True
        )
        return self.get_paginated_response(serializer.data)

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
        page = self.paginate_queryset(
            request.user.jobs_as_driver.filter(
                progress=c.JOB_PROGRESS_NOT_STARTED
            )
        )

        serializer = s.JobDataViewSerializer(
            page,
            many=True
        )

        return self.get_paginated_response(serializer.data)

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
        detail=False, url_path='bill-documents'
    )
    def get_all_job_documents(self, request, pk=None):
        bill_type = request.query_params.get('type', 'all')

        page = self.paginate_queryset(
            request.user.jobs_as_driver.filter(
                ~Q(progress=c.JOB_PROGRESS_NOT_STARTED)
            )
        )

        serializer = s.JobBillViewSerializer(
            page,
            context={'request': request, 'bill_type': bill_type},
            many=True
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True, url_path='bill-documents'
    )
    def bill_documents(self, request, pk=None):
        bill_type = request.query_params.get('type', 'all')
        job = self.get_object()

        return Response(
            s.JobDoneSerializer(
                job,
                context={'request': request, 'bill_type': bill_type}
            ).data,
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


class JobReportViewSet(viewsets.ModelViewSet):

    queryset = m.JobReport.objects.all()
    serializer_class = s.DriverJobReportSerializer

    @action(detail=False, url_path='me')
    def me(self, request):
        page = self.paginate_queryset(
            request.user.report.all()
        )
        serializer = s.JobReportSEr(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

        return Response(
            request.user.report.all()
        )
        return request.user
