from django.urls import path
from . import views

urlpatterns = [
    path("old_predict", views.prediction_endpoint, name="old_predict"),
    path("current_weather", views.current_weather_endpoint, name="current_weather"),
    path("chart", views.chart_endpoint, name="chart"),
    path("location-prediction", views.predict, name="location_prediction"),
    path("location_prediction_endpoint", views.location_prediction_endpoint, name="location_prediction_endpoint"),
    path("roadwatch", views.roadwatch_endpoint, name="roadwatch")
]
