from django.urls import path
from . import views

urlpatterns = [
    path("predict", views.prediction_endpoint, name="predict"),
    path("current_weather", views.current_weather_endpoint, name="current_weather"),
    path("chart", views.chart_endpoint, name="chart"),
    path("make_prediction_using_coordinates", views.make_prediction_using_coordinates, name="make_prediction_using_coordinates"),
    # path("make_prediction_using_coordinates", views.make_prediction_using_coordinates, name="make_prediction_using_coordinates"),
    path("stop_timer", views.stop_timer, name="stop_timer"),
    # path("get_graph_values", views.get_graph_values, name="get_graph_values")
]
