"""
Websocket urlpatterns.
"""
from django.urls import re_path

from . import consumer

ws_urlpatterns = [
    re_path(r'ws/stocks/(?P<ticker>\w+)/$', consumer.StockConsumer.as_asgi()),
]
