from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(
        r'^ws/notification/(?P<user_pk>[^/]+)/$',
        consumers.NotificationConsumer
    ),
    url(
        r'^ws/position/(?P<user_pk>[^/]+)/$',
        consumers.PositionConsumer
    ),
    url(
        r'^ws/jobposition/(?P<user_pk>[^/]+)/orders/(?P<order_pk>[^/]+)/$',
        consumers.CustomerJobPositionConsumer
    ),
]
