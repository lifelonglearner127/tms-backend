from rest_framework import viewsets

from . import models as m
from . import serializers as s


class JobViewSet(viewsets.ModelViewSet):
    """
    Job Viewset
    """
    queryset = m.Job.objects.all()
    serializer_class = s.JobSerializer
