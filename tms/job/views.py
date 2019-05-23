from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..core import constants
from . import models as m
from . import serializers as s


class JobViewSet(viewsets.ModelViewSet):
    """
    """
    queryset = m.Job.objects.all()
    serializer_class = s.JobSerializer

    def create(self, request):
        data = request.data
        for job in data:
            context = {
                'mission': job.pop('mission')
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

    @action(detail=False, url_path='done')
    def previous_jobs(self, request):
        serializer = self.serializer_class(
            m.Job.objects.filter(finished_at__lte=datetime.now()),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='current')
    def progress_jobs(self, request):
        serializer = self.serializer_class(
            m.Job.objects.filter(
                ~(Q(progress=constants.JOB_PROGRESS_NOT_STARTED) |
                  Q(progress=constants.JOB_PROGRESS_COMPLETE))
            ).first()
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, url_path='future')
    def future_jobs(self, request):
        serializer = self.serializer_class(
            m.Job.objects.filter(progress=constants.JOB_PROGRESS_NOT_STARTED),
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
