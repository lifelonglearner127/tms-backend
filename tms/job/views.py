from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants
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
        data = request.data
        for job in data:
            context = {
                'missions': job.pop('missions', None)
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

    def update(self, request):
        data = request.data
        for job in data:
            context = {
                'missions': job.pop('missions', None)
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
                ~(Q(progress=constants.JOB_PROGRESS_NOT_STARTED) |
                  Q(progress=constants.JOB_PROGRESS_COMPLETE))
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
                progress=constants.JOB_PROGRESS_NOT_STARTED
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
