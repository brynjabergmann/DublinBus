from django.urls import path
from . import views

urlpatterns = [
    path("predict", views.prediction_endpoint, name="predict"),
    path("current_weather", views.current_weather_endpoint, name="current_weather")
]
