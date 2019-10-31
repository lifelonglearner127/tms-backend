from django.contrib.auth import get_user_model
from django.db.models import Q
from ..core.constants import (
    USER_TYPE_ADMIN, USER_TYPE_STAFF, USER_TYPE_SECURITY_OFFICER,
    USER_TYPE_DRIVER, USER_TYPE_ESCORT, USER_TYPE_GUEST_DRIVER, USER_TYPE_GUEST_ESCORT,
    USER_TYPE_CUSTOMER,
)


UserModel = get_user_model()


class TMSAuthenticationBackend:
    """
    Authentication against either phone number or username
    """
    def authenticate(
        self, request, username=None, password=None,
        user_type='', device_token=None
    ):
        # if username.isdigit():
        #     kwargs = {'mobile': username}
        # else:
        # #     kwargs = {'username': username}

        query_filter = Q(username=username)

        if user_type == 'D':
            query_filter &= Q(user_type__in=[
                USER_TYPE_DRIVER, USER_TYPE_ESCORT, USER_TYPE_GUEST_DRIVER, USER_TYPE_GUEST_ESCORT
            ])
        elif user_type == 'C':
            query_filter &= Q(user_type=USER_TYPE_CUSTOMER)
        else:
            query_filter &= Q(user_type__in=[
                USER_TYPE_ADMIN, USER_TYPE_STAFF, USER_TYPE_SECURITY_OFFICER
            ])

        user = UserModel.objects.filter(query_filter).first()
        if user is not None:
            if user.check_password(password):
                if device_token is not None:
                    user.device_token = device_token
                    user.save()
                return user
        else:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
