from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets, status
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
            driver_id = deliver.get('driver', None)
            escort_id = deliver.get('escort', None)
            vehicle_id = deliver.get('vehicle', None)
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
                    job['total_weight'] += int(mission_weight)
                    new_job = False
                    continue

            if new_job:
                jobs.append({
                    'driver': driver_id,
                    'escort': escort_id,
                    'vehicle': vehicle_id,
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
        serializer = self.serializer_class(
            request.user.staff_profile.jobs_as_primary.filter(
                finished_at__lte=datetime.now()
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
        serializer = self.serializer_class(
            request.user.staff_profile.jobs_as_primary.filter(
                ~(Q(progress=c.JOB_PROGRESS_NOT_STARTED) |
                  Q(progress=c.JOB_PROGRESS_COMPLETE))
            ).first()
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False, url_path='future',
        permission_classes=[IsDriverOrEscortUser]
    )
    def future_jobs(self, request):
        serializer = self.serializer_class(
            request.user.staff_profile.jobs_as_primary.filter(
                progress=c.JOB_PROGRESS_NOT_STARTED
            ),
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
