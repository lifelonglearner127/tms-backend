from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings

from ...core import constants


UserModel = get_user_model()


class LoginTestSet(APITestCase):

    def setUp(self):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        self.admin = UserModel.objects.create(
            username='admin',
            phone_number='123',
            password='gibupjo127',
            role=constants.USER_ROLE_ADMIN
        )
        payload = jwt_payload_handler(self.admin)
        self.admin_token = jwt_encode_handler(payload)

        self.staff = UserModel.objects.create(
            username='staff',
            phone_number='456',
            password='gibupjo127',
            role=constants.USER_ROLE_STAFF
        )
        payload = jwt_payload_handler(self.staff)
        self.staff_token = jwt_encode_handler(payload)

        self.driver = UserModel.objects.create(
            username='driver',
            phone_number='789',
            password='gibupjo127',
            role=constants.USER_ROLE_DRIVER
        )
        payload = jwt_payload_handler(self.driver)
        self.driver_token = jwt_encode_handler(payload)

        self.escort = UserModel.objects.create(
            username='escrot',
            phone_number='123456',
            password='gibupjo127',
            role=constants.USER_ROLE_ESCORT
        )
        payload = jwt_payload_handler(self.escort)
        self.escort_token = jwt_encode_handler(payload)

        self.customer = UserModel.objects.create(
            username='customer',
            phone_number='456789',
            password='gibupjo127',
            role=constants.USER_ROLE_CUSTOMER
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
