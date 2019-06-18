"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import json
import paho.mqtt.client as mqtt
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from rest_framework_swagger.views import get_swagger_view
from tms.vehicle.models import Vehicle

schema_view = get_swagger_view(title='TMS API')
urlpatterns = [
    path(
        '', schema_view
    ),
    path(
        'admin/', admin.site.urls
    ),
    path(
        'api/',
        include(
            ('tms.account.urls', 'account'),
            namespace='account'
        )
    ),
    path(
        'api/',
        include(
            ('tms.info.urls', 'info'),
            namespace='info'
        )
    ),
    path(
        'api/',
        include(
            ('tms.vehicle.urls', 'vehicle'),
            namespace='vehicle'
        )
    ),
    path(
        'api/',
        include(
            ('tms.order.urls', 'order'),
            namespace='order'
        )
    ),
    path(
        'api/',
        include(
            ('tms.job.urls', 'job'),
            namespace='job'
        )
    ),
    path(
        'api/',
        include(
            ('tms.road.urls', 'road'),
            namespace='road'
        )
    ),
    path(
        'api/',
        include(
            ('tms.notification.urls', 'notification'),
            namespace='notification'
        )
    ),
    path(
        'api/hr/',
        include(
            ('tms.hr.urls', 'hr'),
            namespace='hr'
        )
    ),
    path(
        'api/finance/',
        include(
            ('tms.finance.urls', 'finance'),
            namespace='finance'
        )
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )


def on_message_locations(client, userdata, msg):
    payload = msg.payload.decode('utf-8')
    payload = json.loads(payload)

    for item in payload['data']:
        plate_num = item['plateNum']
        longitude = item['lng']
        latitude = item['lat']
        speed = item['speed']
        try:
            vehicle = Vehicle.objects.get(plate_num=plate_num)
            vehicle.longitude = longitude
            vehicle.latitude = latitude
            vehicle.speed = speed
            vehicle.save()
        except Vehicle.DoesNotExist:
            pass


client = mqtt.Client(client_id=settings.G7_MQTT_POSITION_CLIENT_ID)
client.message_callback_add(
    settings.G7_MQTT_POSITION_TOPIC, on_message_locations
)
client.username_pw_set(
    settings.G7_MQTT_POSITION_ACCESS_ID,
    password=settings.G7_MQTT_POSITION_SECRET
)

client.connect(settings.G7_MQTT_HOST, 1883, 60)
client.subscribe(settings.G7_MQTT_POSITION_TOPIC, 0)
client.loop_start()
