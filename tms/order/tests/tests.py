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

        self.valid_create_product_payload = {
            "products": [
                {
                    "product": {
                        "id": 1
                    },
                    "total_weight": 5,
                    "unloading_stations": [
                        {
                            "weight": 3,
                            "unloading_station": {
                                "id": 1
                            }
                        }
                    ]
                }
            ],
            "loading_station": {
                "id": 1
            },
            "alias": "Order",
            "rest_place": "Rest place",
            "change_place": "Change",
            "assignee": 2,
            "customer": 3
        }

        self.invalid_create_product_payload = {

        }

    def test_create_order(self):
        """
         - create order by admin - success
         - create order by staff - success
         - create order by driver - forbidden
         - create order by escort - forbidden
         - create order by customer - success
        """
        pass

    def test_update_order(self):
        """
         - update order by admin - success
         - update order by staff - success
         - update order by driver - forbidden
         - update order by escort - forbidden
         - update order by customer - success
        """
        pass

    def test_retrieve_order(self):
        """
         - retrieve order by admin - success
         - retrieve order by staff - success
         - retrieve order by driver - success
         - retrieve order by escort - success
         - retrieve order by customer - success
        """
        pass

    def test_list_order(self):
        """
         - retrieve order by admin - success
         - retrieve order by staff - success
         - retrieve order by driver - success
         - retrieve order by escort - success
         - retrieve order by customer - success
        """
        pass
