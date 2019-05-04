from rest_framework import viewsets
from rest_framework.views import APIView
from .permissions import IsAccountStaffOrReadOnly


class StaffViewSet(viewsets.ModelViewSet):
    """
    Vieweset only allowed for admin or staff permission
    """
    permission_classes = [IsAccountStaffOrReadOnly]


class StaffAPIView(APIView):
    """
    APIView only allowed for admin or staff permission
    """
    permission_classes = [IsAccountStaffOrReadOnly]
