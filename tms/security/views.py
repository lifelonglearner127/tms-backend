from rest_framework import status
from rest_framework.response import Response

# models
from . import models as m

# serializers
from . import serializers as s

# views
from ..core.views import TMSViewSet


class CompanyPolicyViewSet(TMSViewSet):

    queryset = m.CompanyPolicy.objects.all()
    serializer_class = s.CompanyPolicySerializer

    def create(self, request):
        author = request.data.pop('author', None)

        if author is not None:
            pass
        else:
            author = request.user

        serializer = s.CompanyPolicySerializer(
            data=request.data,
            context={
                'author': author
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        author = request.data.pop('author', None)

        if author is not None:
            pass
        else:
            author = request.user

        serializer = s.CompanyPolicySerializer(
            instance,
            data=request.data,
            context={
                'author': author
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class SecurityKnowledgeViewSet(TMSViewSet):

    queryset = m.SecurityKnowledge.objects.all()
    serializer_class = s.SecurityKnowledgeSerializer

    def create(self, request):
        author = request.data.pop('author', None)

        if author is not None:
            pass
        else:
            author = request.user

        serializer = s.SecurityKnowledgeSerializer(
            data=request.data,
            context={
                'author': author
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def update(self, request, pk=None):
        instance = self.get_object()
        author = request.data.pop('author', None)

        if author is not None:
            pass
        else:
            author = request.user

        serializer = s.SecurityKnowledgeSerializer(
            instance,
            data=request.data,
            context={
                'author': author
            }
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
