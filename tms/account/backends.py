from django.contrib.auth import get_user_model


UserModel = get_user_model()


class TMSAuthenticationBackend:
    def authenticate(self, request, username=None, password=None):
        if username.isdigit():
            kwargs = {'phone_number': username}
        else:
            kwargs = {'username': username}
        try:
            user = UserModel.objects.get(**kwargs)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
