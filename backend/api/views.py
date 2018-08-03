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
from raven import Client
from api.models import DarkskyCurrentWeather as weather

client = Client('https://1e979ddecb1641ce81a0468314902d26:e894e38ec1f64c43af6876f76a3d2959@sentry.io/1249736')


def current_weather(request):

    try:
        first_row_of_table_as_dict = weather.objects.all().order_by("-timestamp")[:1].values()[0]
        return JsonResponse(first_row_of_table_as_dict)
    except CurrentWeatherError:
        client.captureException()


def forecast(request):

    try:
        hour = dt.datetime.now().hour
        day = dt.datetime.today().weekday()
        with connection.cursor() as cursor:
            cursor.execute("SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = %s AND hour = %s;", [day, hour])
            row = cursor.fetchone()
            dow = row[0]
            hour = row[1]
            temp = row[2]
            rain = row[3]
            forecast = {"dow": dow, "hour": hour, "temp": temp, "rain": rain}
            return JsonResponse(forecast)
    except ForecastWeatherError:
        client.captureException()

def daily_forecast(request):
    # The user will be able to select a date, which will translate into day below
    try:
        day = dt.datetime.today().weekday()
        daily_forecast = []
        for hour in range(24):
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = %s AND hour = %s;",
                    [day, hour])
                row = cursor.fetchone()
                dow = row[0]
                hour = row[1]
                temp = row[2]
                rain = row[3]
                hourly_forecast = {"dow": dow, "hour": hour, "temp": temp, "rain": rain}
                daily_forecast.append(hourly_forecast)
        all_day_weather = {"all_day_weather": daily_forecast}
        return JsonResponse(all_day_weather)
    except DailyForecastError:
        client.captureException()


@csrf_exempt    # Can remove in production, needed for testing
def make_prediction(request):
    try:
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

        with open(f"api/models/GBR_school_2017_{values['route']}_{direction}.pkl", "rb") as f:
            cucumber = pickle.load(f)

        model = cucumber[0]
        max_stops = cucumber[1]

        end_to_end = int(round(model.predict(prediction_inputs)[0]))    # Predict time from start to finish

        segment = int(end_to_end * ((last_stop - first_stop) / max_stops))

        # # # # # # # # # # # # # # # # # # # # # # # #
        # TODO: THIS IS FOR EVALUATION PURPOSES ONLY  #
        # TODO: AND SHOULD BE REMOVED BEFORE RELEASE  #
        # # # # # # # # # # # # # # # # # # # # # # # #

        if values["username"]:
            with open(f"{values['username'].lower()}_timer.txt", "w") as f:
                f.write(f"{segment}\n")
                f.write(f"{round(dt.datetime.timestamp(dt.datetime.now()))}\n")

        prediction = {"result": segment, "message": f"Thank you {values['username']}; enjoy your trip!"}
        return JsonResponse(prediction)
    except TestMakePredictionError:
        client.captureException()



@csrf_exempt
def stop_location(request):

    try:
        values = json.loads(request.body.decode('utf-8'))
        with connection.cursor() as cursor:
            cursor.execute("SELECT lat, `long` FROM static_bus_data WHERE stoppointid = %s LIMIT 1", [int(values["stop"])])
            row = cursor.fetchone()
            lat = row[0]
            lng = row[1]

        return JsonResponse({"lat": lat, "lng": lng})
    except StopLocationRequestError:
        client.captureException()


@csrf_exempt
def stop_timer(request):

    try:
        username = json.loads(request.body.decode("utf-8"))["username"]

        with open(f"{username.lower()}_timer.txt") as f:
            x = f.readlines()

        prediction = int(x[0])
        actual = round((dt.datetime.timestamp(dt.datetime.now()) - int(x[1])) / 60)
        percentage = round(((actual-prediction)/prediction) * 100, 2)

        return JsonResponse({"prediction": prediction, "actual": actual, "percentage": percentage})
    except StopTimerRequestError:
        client.captureException()


@csrf_exempt
def fare_finder(trip, stages):
        # Do not use this function for any Xpress service and route 90
        # Xpress services charge leap at 2.90 and cash at 3.65
        # Route 90 charges leap at 1.50 and cash at 2.10
    try:
        leap = "€2.15"
        cash = "€2.85"
        stages = len(list(set(trip).intersection(stages)))
        if stages < 4:
            leap = "€1.50"
            cash = "€2.10"
        if stages > 12:
            leap = "€2.60"
            cash = "€3.30"
        return([leap, cash])
    except FareFinderError:
        client.captureException()





