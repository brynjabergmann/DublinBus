from django.urls import path
from . import views

urlpatterns = [
    path("current_weather", views.current_weather, name="current_weather"),
    path("make_prediction", views.make_prediction, name="make_prediction"),
    path("stop_location", views.stop_location, name="stop_location"),
    path("forecast", views.forecast, name="forecast"),
    path("daily_forecast", views.daily_forecast, name="daily_forecast"),
]
