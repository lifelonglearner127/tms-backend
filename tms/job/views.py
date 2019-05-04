from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from ..core import constants
from .models import Job
from .serializers import JobSerializer


class JobViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):

    queryset = Job.objects.all()
    serializer_class = JobSerializer
