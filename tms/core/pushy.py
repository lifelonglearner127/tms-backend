import json
import requests
from django.conf import settings


class PushyAPI:

    @staticmethod
    def sendPushNotification(data, to, options):
        # Insert your Pushy Secret API Key here
        apiKey = settings.PUSHY_SECRET_KEY

        # Default post data to provided options or empty object
        postData = options or {}

        # Set notification payload and recipients
        postData['to'] = to
        postData['data'] = data

        try:
            r = requests.post(
                'https://api.pushy.me/push?api_key=' + apiKey,
                data=json.dumps(postData),
                headers={
                    'Content-Type': 'application/json'
                }
            )
        except requests.exceptions.HTTPError as e:
            err_str = "Pushy API returned HTTP error " + str(e.code) + \
                ": " + e.read()
            print(err_str)
            # TODO logging instead of printing
