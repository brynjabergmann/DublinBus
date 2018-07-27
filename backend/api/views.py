from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import json
import pickle
import pandas as pd
import os
import sklearn
import datetime as dt

def current_weather(request):
    from api.models import DarkskyCurrentWeather as weather
    first_row_of_table_as_dict = weather.objects.all().order_by("-timestamp")[:1].values()[0]
    return JsonResponse(first_row_of_table_as_dict)

def forecast(request):
    values = json.loads(request.body.decode('utf-8'))
    hour = values["hour"]
    day = dt.datetime.today().weekday()

    with connection.cursor() as cursor:
        cursor.execute("SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = %s AND hour = %s;", [day, hour])
        row = cursor.fetchone()
        dow = row[0]
        hour = row[1]
        temp = row[2]
        rain = row[3]
        forecast = { "dow" : dow, "hour" : hour, "temp" : temp, "rain" : rain }   
        return JsonResponse(forecast)

@csrf_exempt    # Can remove in production, needed for testing
def make_prediction(request):
    # Convert JSON string passed by browser to Python dictionary:
    values = json.loads(request.body.decode('utf-8'))

    # Quick way to convert JS's day of week into a categorical feature:
    days_list = [0, 0, 0, 0, 0, 0, 0]
    days_list[values["day"]] = 1

    # Create a pandas dataframe to be fed into the prediction model
    prediction_inputs = pd.DataFrame({
        "avg_H": [values["hour"]],
        "DOW_Monday": [days_list[0]],
        "DOW_Tuesday": [days_list[1]],
        "DOW_Wednesday": [days_list[2]],
        "DOW_Thursday": [days_list[3]],
        "DOW_Friday": [days_list[4]],
        "DOW_Saturday": [days_list[5]],
        "DOW_Sunday": [days_list[6]],
        "temp": [values["temp"]],
        "precip_intensity": [values["rain"]]
    })

    with connection.cursor() as cursor:
        cursor.execute("SELECT direction, stop_on_route FROM combined_2017 WHERE line_id = %s AND stop_number = %s LIMIT 1;", [values["route"], values["startStop"]])
        row = cursor.fetchone()
        direction = row[0]
        first_stop = row[1]

        # Get last stop progression number
        cursor.execute("SELECT stop_on_route FROM combined_2017 WHERE line_id = %s AND stop_number = %s LIMIT 1;", [values["route"], values["endStop"]])
        row = cursor.fetchone()
        last_stop = row[0]

    with open(f"api/models/GBR_March_2017_{values['route']}_{direction}.pkl", "rb") as f:
        cucumber = pickle.load(f)

    model = cucumber[0]
    max_stops = cucumber[1]

    end_to_end = int(round(model.predict(prediction_inputs)[0]))    # Predict time from start to finish

    segment = int(end_to_end * ((last_stop - first_stop) / max_stops))
    prediction = {"result": segment}

    return JsonResponse(prediction)


@csrf_exempt
def first_stop(request):
    values = json.loads(request.body.decode("utf-8"))
    with connection.cursor() as cursor:
        cursor.execute("SELECT stop_on_route, direction FROM combined_2017 WHERE line_id = %s AND stop_number = %s LIMIT 1;", [values["route"], values["start_stop"]])
        row = cursor.fetchone()


@csrf_exempt
def stop_location(request):
    values = json.loads(request.body.decode('utf-8'))
    with connection.cursor() as cursor:
        cursor.execute("SELECT lat, `long` FROM static_bus_data WHERE stoppointid = %s LIMIT 1", [int(values["stop"])])
        row = cursor.fetchone()
        lat = row[0]
        lng = row[1]

    return JsonResponse({"lat": lat, "lng": lng})
