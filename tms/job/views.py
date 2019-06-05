from django.db.models import Q
from django.utils import timezone as datetime
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants as c
from ..core.permissions import IsDriverOrEscortUser
from . import models as m
from . import serializers as s


class JobViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = m.Job.objects.all()
    serializer_class = s.JobSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return s.JobSerializer
        else:
            return s.JobDataSerializer

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
                    job['total_weight'] += int(mission_weight)
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
                    'total_weight': int(mission_weight)
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
        detail=False, url_path='done',
        permission_classes=[IsDriverOrEscortUser]
    )
    def previous_jobs(self, request):
        serializer = s.JobDataSerializer(
            request.user.driver_profile.jobs.filter(
                finished_on__lte=datetime.now()
            ),
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
        job = request.user.driver_profile.jobs.filter(
            ~(Q(progress=c.JOB_PROGRESS_NOT_STARTED) |
                Q(progress=c.JOB_PROGRESS_COMPLETE))
        ).first()

        if job is None:
            job = request.user.driver_profile.jobs.filter(
                progress=c.JOB_PROGRESS_NOT_STARTED
            ).first()

        if job is not None:
            ret = s.JobDataSerializer(job).data
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
        serializer = s.JobDataSerializer(
            request.user.driver_profile.jobs.filter(
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

        if progress == c.JOB_PROGRESS_NOT_STARTED:
            job.started_on = datetime.now()
            job.progress = c.JOB_PROGRESS_TO_LOADING_STATION

        elif progress == c.JOB_PROGRESS_TO_LOADING_STATION:
            job.arrived_loading_station_on = datetime.now()
            job.progress = c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION

        elif progress == c.JOB_PROGRESS_ARRIVED_AT_LOADING_STATION:
            job.started_loading_on = datetime.now()
            job.progress = c.JOB_PROGRESS_LOADING_AT_LOADING_STATION

        elif progress == c.JOB_PROGRESS_LOADING_AT_LOADING_STATION:
            job.finished_loading_on = datetime.now()
            job.progress = c.JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION

        elif progress == c.JOB_PROGRESS_FINISH_LOADING_AT_LOADING_STATION:
            job.departure_loading_station_on = datetime.now()
            job.progress = c.JOB_PROGRESS_TO_QUALITY_STATION

        elif progress == c.JOB_PROGRESS_TO_QUALITY_STATION:
            job.arrived_quality_station_on = datetime.now()
            job.progress = c.JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION

        elif progress == c.JOB_PROGRESS_ARRIVED_AT_QUALITY_STATION:
            job.started_checking_on = datetime.now()
            job.progress = c.JOB_PROGRESS_CHECKING_AT_QUALITY_STATION

        elif progress == c.JOB_PROGRESS_CHECKING_AT_QUALITY_STATION:
            job.finished_checking_on = datetime.now()
            job.progress = c.JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION

        elif progress == c.JOB_PROGRESS_FINISH_CHECKING_AT_QUALITY_STATION:
            job.departure_quality_station_on = datetime.now()
            job.progress = c.JOB_PROGRESS_TO_UNLOADING_STATION

        elif progress == c.JOB_PROGRESS_TO_UNLOADING_STATION:
            current_mission = job.mission_set.filter(
                is_completed=False
            ).first()
            current_mission.arrived_station_on = datetime.now()
            current_mission.save()
            job.progress = c.JOB_PRGORESS_ARRIVED_AT_UNLOADING_STATION

        elif progress == c.JOB_PRGORESS_ARRIVED_AT_UNLOADING_STATION:
            current_mission = job.mission_set.filter(
                is_completed=False
            ).first()
            current_mission.started_unloading_on = datetime.now()
            current_mission.save()
            job.progress = c.JOB_PROGRESS_UNLOADING_AT_UNLOADING_STATION

        elif progress == c.JOB_PROGRESS_UNLOADING_AT_UNLOADING_STATION:
            current_mission = job.mission_set.filter(
                is_completed=False
            ).first()
            current_mission.finished_unloading_on = datetime.now()
            current_mission.save()
            job.progress = c.JOB_PROGRESS_FINISH_UNLOADING_AT_UNLOADING_STATION

        elif progress == c.JOB_PROGRESS_FINISH_UNLOADING_AT_UNLOADING_STATION:
            current_mission = job.mission_set.filter(
                is_completed=False
            ).first()
            current_mission.is_completed = True
            current_mission.departure_station_on = datetime.now()
            current_mission.save()

            if job.mission_set.filter(is_completed=False).exists():
                job.progress = c.JOB_PROGRESS_TO_UNLOADING_STATION
            else:
                job.progress = c.JOB_PROGRESS_COMPLETE
                job.finished_on = datetime.now()

        else:
            return Response(
                s.JobProgressSerializer(job).data,
                status=status.HTTP_200_OK
            )

        job.save()

        return Response(
            s.JobProgressSerializer(job).data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=True, url_path='upload', methods=['post'],
        permission_classes=[IsDriverOrEscortUser]
    )
    def upload(self, request, pk=None):
        data = request.data
        data['job'] = pk
        serializer = s.JobBillDocumentSerializer(
            data=data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True, url_path='documents',
        permission_classes=[IsDriverOrEscortUser]
    )
    def documents(self, request, pk=None):
        job = self.get_object()
        category = request.query_params.get('category', None)

        if category is not None:
            serializer = s.JobBillDocumentSerializer(
                job.bills.filter(category=category),
                many=True
            )
        else:
            serializer = s.JobBillDocumentSerializer(
                job.bills.all(),
                many=True
            )

        return Response(
            serializer.data,
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


class DriverNotificationViewSet(mixins.RetrieveModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):
    """
    """
    permission_classes = [IsDriverOrEscortUser]
    serializer_class = s.DriverNotificationSerializer

    def get_queryset(self):
        return self.request.user.driver_profile.notifications.all()