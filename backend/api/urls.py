from django.urls import path
from . import views

urlpatterns = [
    path("predict", views.prediction_endpoint, name="predict"),
    path("current_weather", views.current_weather_endpoint, name="current_weather"),
    path("chart", views.chart_endpoint, name="chart"),
    path("location-prediction", views.predict_from_locations, name="location_prediction"),
    path("location_prediction_endpoint", views.location_prediction_endpoint, name="location_prediction_endpoint")
]
