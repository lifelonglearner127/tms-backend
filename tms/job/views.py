from rest_framework import viewsets, status
from rest_framework.response import Response

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


class MissionViewSet(viewsets.ModelViewSet):
    """
    """
    serializer_class = s.MissionSerializer

    def get_queryset(self):
        return m.Mission.objects.filter(
            job__id=self.kwargs['job_pk']
        )
