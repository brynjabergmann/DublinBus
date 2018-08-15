from django.urls import path
from . import views

urlpatterns = [
    path("predict", views.prediction_endpoint, name="predict"),
    path("current_weather", views.current_weather_endpoint, name="current_weather"),
    path("chart", views.chart_endpoint, name="chart"),
    path("make_prediction_using_coordinates", views.make_prediction_using_coordinates, name="make_prediction_using_coordinates"),
    path("location-prediction", views.predict_from_locations, name="location_prediction")
]
