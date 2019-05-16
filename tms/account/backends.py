from django.contrib.auth import get_user_model


UserModel = get_user_model()


class TMSAuthenticationBackend:
    """
    Authentication against either phone number or username
    """
    def authenticate(
        self, request, username=None, password=None, device_token=None
    ):
        if username.isdigit():
            kwargs = {'mobile': username}
        else:
            kwargs = {'username': username}
        try:
            user = UserModel.objects.get(**kwargs)
            if user.check_password(password):
                if device_token is not None:
                    user.device_token = device_token
                    user.save()
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
