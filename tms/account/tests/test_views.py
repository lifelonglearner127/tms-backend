from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings

from ...core import constants as c


UserModel = get_user_model()


class LoginTestSet(APITestCase):

    def setUp(self):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        self.admin = UserModel.objects.create(
            username='admin',
            mobile='123',
            password='gibupjo127',
            user_type=c.USER_TYPE_ADMIN
        )
        payload = jwt_payload_handler(self.admin)
        self.admin_token = jwt_encode_handler(payload)

        self.staff = UserModel.objects.create(
            username='staff',
            mobile='456',
            password='gibupjo127',
            user_type=c.USER_TYPE_STAFF
        )
        payload = jwt_payload_handler(self.staff)
        self.staff_token = jwt_encode_handler(payload)

        self.driver = UserModel.objects.create(
            username='driver',
            mobile='789',
            password='gibupjo127',
            user_type=c.USER_TYPE_DRIVER
        )
        payload = jwt_payload_handler(self.driver)
        self.driver_token = jwt_encode_handler(payload)

        self.escort = UserModel.objects.create(
            username='escrot',
            mobile='123456',
            password='gibupjo127',
            user_type=c.USER_TYPE_ESCORT
        )
        payload = jwt_payload_handler(self.escort)
        self.escort_token = jwt_encode_handler(payload)

        self.customer = UserModel.objects.create(
            username='customer',
            mobile='456789',
            password='gibupjo127',
            user_type=c.USER_TYPE_CUSTOMER
        )
        payload = jwt_payload_handler(self.customer)
        self.customer_token = jwt_encode_handler(payload)

    def login_from_web(self):
        """
         - login admin - success
         - login staff - success
         - login driver - fail
         - login escort - fail
         - login customer - fail
        """
        pass

    def login_from_driver_app(self):
        """
         - login admin - fail
         - login staff - fail
         - login driver - success
         - login escort - fail
         - login customer - fail
        """
        pass

    def login_from_customer_app(self):
        """
         - login admin - fail
         - login staff - fail
         - login driver - fail
         - login escort - fail
         - login customer - success
        """
        pass

    def login_from_admin_app(self):
        """
         - login admin - success
         - login staff - success
         - login driver - fail
         - login escort - fail
         - login customer - fail
        """
        pass
