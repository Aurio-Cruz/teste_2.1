from django.urls import path

from.views import Indexview

urlpatterns = [
    path("index/", Indexview.as_view(), name = "index"),
]