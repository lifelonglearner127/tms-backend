from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings

from ...core import constants


UserModel = get_user_model()


class ProductViewSetTest(APITestCase):
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

        self.valid_create_product_payload = {

        }

        self.invalid_create_product_payload = {

        }

    def test_create_product(self):
        """
         - create product by admin - success
         - create product by staff - success
         - create product by driver - forbidden
         - create product by escort - forbidden
         - create product by customer - forbidden
        """
        pass

    def test_update_product(self):
        """
         - update product by admin - success
         - update product by staff - success
         - update product by driver - forbidden
         - update product by escort - forbidden
         - update product by customer - forbidden
        """
        pass

    def test_retrieve_product(self):
        """
         - retrieve product by admin - success
         - retrieve product by staff - success
         - retrieve product by driver - success
         - retrieve product by escort - success
         - retrieve product by customer - success
        """
        pass

    def test_list_product(self):
        """
         - retrieve product by admin - success
         - retrieve product by staff - success
         - retrieve product by driver - success
         - retrieve product by escort - success
         - retrieve product by customer - success
        """
        pass
