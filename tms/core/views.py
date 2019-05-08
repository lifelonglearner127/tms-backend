from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .permissions import IsStaffUser
from .serializers import ChoiceSerializer


class StaffViewSet(viewsets.ModelViewSet):
    """
    Vieweset only allowed for admin or staff permission
    """
    permission_classes = [IsStaffUser]


class StaffAPIView(APIView):
    """
    APIView only allowed for admin or staff permission
    """
    permission_classes = [IsStaffUser]


class ChoicesView(StaffAPIView):
    """
    APIView for returning backend contant choices
    """
    static_choices = ()

    def get(self, request):
        choices = []
        for (slug, name) in self.static_choices:
            choices.append(
                {
                    'value': slug,
                    'text': name
                }
            )

        serializer = ChoiceSerializer(
            choices,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class ShortAPIView(StaffAPIView):
    """
    View to list short data of specified model
    """
    model_class = None
    serializer_class = None

    def get_queryset(self):
        return self.model_class.objects.all()

    def get(self, request):
        serializer = self.serializer_class(
            self.get_queryset(),
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
