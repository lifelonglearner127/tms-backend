from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings

from ...core import constants


UserModel = get_user_model()


class VehicleViewSetTest(APITestCase):
    def setUp(self):

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        self.admin = UserModel.objects.create(
            username='admin',
            mobile='123',
            password='gibupjo127',
            role=constants.USER_ROLE_ADMIN
        )
        payload = jwt_payload_handler(self.admin)
        self.admin_token = jwt_encode_handler(payload)

        self.staff = UserModel.objects.create(
            username='staff',
            mobile='456',
            password='gibupjo127',
            role=constants.USER_ROLE_STAFF
        )
        payload = jwt_payload_handler(self.staff)
        self.staff_token = jwt_encode_handler(payload)

        self.driver = UserModel.objects.create(
            username='driver',
            mobile='789',
            password='gibupjo127',
            role=constants.USER_ROLE_DRIVER
        )
        payload = jwt_payload_handler(self.driver)
        self.driver_token = jwt_encode_handler(payload)

        self.escort = UserModel.objects.create(
            username='escrot',
            mobile='123456',
            password='gibupjo127',
            role=constants.USER_ROLE_ESCORT
        )
        payload = jwt_payload_handler(self.escort)
        self.escort_token = jwt_encode_handler(payload)

        self.customer = UserModel.objects.create(
            username='customer',
            mobile='456789',
            password='gibupjo127',
            role=constants.USER_ROLE_CUSTOMER
        )
        payload = jwt_payload_handler(self.customer)
        self.customer_token = jwt_encode_handler(payload)

        self.valid_create_vehicle_payload = {

        }

        self.invalid_create_vehicle_payload = {

        }

    def test_create_vehicle(self):
        """
         - create vehicle by admin - success
         - create vehicle by staff - success
         - create vehicle by driver - forbidden
         - create vehicle by escort - forbidden
         - create vehicle by customer - forbidden
        """
        pass

    def test_update_vehicle(self):
        """
         - update vehicle by admin - success
         - update vehicle by staff - success
         - update vehicle by driver - forbidden
         - update vehicle by escort - forbidden
         - update vehicle by customer - forbidden
        """
        pass

    def test_retrieve_vehicle(self):
        """
         - retrieve vehicle by admin - success
         - retrieve vehicle by staff - success
         - retrieve vehicle by driver - success
         - retrieve vehicle by escort - success
         - retrieve vehicle by customer - success
        """
        pass

    def test_list_vehicle(self):
        """
         - retrieve vehicle by admin - success
         - retrieve vehicle by staff - success
         - retrieve vehicle by driver - success
         - retrieve vehicle by escort - success
         - retrieve vehicle by customer - success
        """
        pass
