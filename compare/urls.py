from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("api/compare/", views.CompareApiView.as_view(), name="api_compare"),
    path("api/tts/", views.tts_api, name="api_tts"),
]
