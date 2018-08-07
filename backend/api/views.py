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
# from raven import Client

# client = Client('https://1e979ddecb1641ce81a0468314902d26:e894e38ec1f64c43af6876f76a3d2959@sentry.io/1249736')


def main(values: dict):  # TODO: Modify to use Request
    first_stop_list = values["firstStops"]
    last_stop_list = values["lastStops"]
    user_time = values["timestamp"]

    weather = get_weather(user_time)
    temperature = weather[0]
    precipitation = weather[2]

    paths = []
    for first_stop in first_stop_list:
        for last_stop in last_stop_list:
            for path in find_route(first_stop, last_stop):
                paths.append(path)

    timings = []
    for path in paths:
        total_time = 0
        bus_routes_on_path = [*path]
        for i in range(len(bus_routes_on_path)):
            bus_route = bus_routes_on_path[i]

            if "walk" in bus_route:
                total_time += path[i]
            else:
                direction = get_direction(bus_route, path[bus_route][0])
                prediction = end_to_end_prediction(dt.datetime.fromtimestamp(user_time).weekday(),
                                                    dt.datetime.fromtimestamp(user_time - (user_time % 3600) + 3600).hour,  # TODO: This + 3600 is some DST fuckery that will ideally need to be dealt with.
                                                    temperature,
                                                    precipitation,
                                                    bus_route,
                                                    direction,
                                                    True)
                proportion = get_proportion(prediction[0], bus_route, direction, path[bus_route][0], path[bus_route][1], prediction[1])
                total_time += proportion
        timings.append(total_time)

    best_route_index = 0
    fastest_time = 10000
    for index, value in enumerate(timings):
        if value < fastest_time:
            best_route_index = index
            fastest_time = value

    return [fastest_time, paths[best_route_index]]


def get_proportion(end_to_end: int, bus_route: str, direction: int, first_stop: int, last_stop: int, max_stops: int):
    # TODO: Use calculated proportions - Further experiments needed.
    with connection.cursor() as cursor:
        cursor.execute("SELECT stop_on_route FROM combined_2017 WHERE line_id = %s AND stop_number = %s AND direction = %s LIMIT 1;", [bus_route, first_stop, direction])
        stop_one = cursor.fetchone()[0]

        cursor.execute("SELECT stop_on_route FROM combined_2017 WHERE line_id = %s AND stop_number = %s AND direction = %s LIMIT 1;", [bus_route, last_stop, direction])
        stop_two = cursor.fetchone()[0]

    return int(end_to_end * ((stop_two - stop_one) / max_stops))


def get_direction(bus_route: str, bus_stop: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT stop_on_route, direction FROM combined_2017 WHERE line_id = %s AND stop_number = %s LIMIT 1;", [bus_route, bus_stop])
        possible_directions = cursor.fetchall()
        stop_on_route = 1000000
        direction = 0
        for result in possible_directions:
            if result[0] < stop_on_route:
                stop_on_route = result[0]
                direction = result[1]
        return direction


def get_weather(timestamp: int):
    now = dt.datetime.now().timestamp()
    now_hour = now - (now % 3600)
    utc_user_hour = timestamp - (timestamp % 3600)

    with connection.cursor() as cursor:
        if now_hour == utc_user_hour:
            cursor.execute("SELECT temp, icon, precip_intensity FROM DarkSky_current_weather ORDER BY timestamp DESC LIMIT 1;")
            return cursor.fetchone()
        else:
            cursor.execute("SELECT temp, icon, precip_intensity FROM DarkSky_hourly_weather_prediction WHERE time = %s;", [utc_user_hour])
            return cursor.fetchone()


def end_to_end_prediction(day_of_week: int, hour_of_day: int, temperature: float, precipitation: float, bus_route: str, direction: int, school: bool):
    # Quick way to convert JS's day of week into a categorical feature:
    days_list = [0, 0, 0, 0, 0, 0, 0]
    days_list[day_of_week] = 1

    # Create a pandas dataframe to be fed into the prediction model
    # prediction_inputs = pd.DataFrame({
    #     "avg_H": [hour_of_day],
    #     "DOW_Monday": [days_list[0]],
    #     "DOW_Tuesday": [days_list[1]],
    #     "DOW_Wednesday": [days_list[2]],
    #     "DOW_Thursday": [days_list[3]],
    #     "DOW_Friday": [days_list[4]],
    #     "DOW_Saturday": [days_list[5]],
    #     "DOW_Sunday": [days_list[6]],
    #     "temp": [temperature],
    #     "precip_intensity": [precipitation]
    # })

    bus_route = "46A"
    direction = 1
    prediction_inputs = pd.DataFrame({
        "avg_H": [9],
        "DOW_Monday": [0],
        "DOW_Tuesday": [1],
        "DOW_Wednesday": [0],
        "DOW_Thursday": [0],
        "DOW_Friday": [0],
        "DOW_Saturday": [0],
        "DOW_Sunday": [0],
        "temp": [12],
        "precip_intensity": [0.0]
    })

    with open(f"api/models/GBR_school_2017_{bus_route}_{direction}.pkl", "rb") as f:
        cucumber = pickle.load(f)

    model = cucumber[0]
    max_stops = cucumber[1]
    prediction_minutes = int(round(model.predict(prediction_inputs)[0]))
    return [prediction_minutes, max_stops]    # Predict time from start to finish


def find_route(first_stop: int, last_stop: int):
    # TODO: This is unfinished. Right now it only works if the two stops provided share a route.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT one.line_id FROM (SELECT line_id FROM stops_served_by WHERE stop_number = %s) as one, (SELECT line_id FROM stops_served_by WHERE stop_number = %s) as two WHERE one.line_id = two.line_id;", [first_stop, last_stop])
        serves_both = list(cursor.fetchall())
        if serves_both:
            return [{x[0]: (first_stop, last_stop)} for x in serves_both]
        else:
            cursor.execute("SELECT line_id FROM stops_served_by WHERE stop_number = %s;", [first_stop])
            all_routes_first_stop = [x[0] for x in list(cursor.fetchall())]
            cursor.execute("SELECT line_id FROM stops_served_by WHERE stop_number = %s;", [last_stop])
            all_routes_last_stop = [x[0] for x in list(cursor.fetchall())]

            for route in all_routes_first_stop:
                cursor.execute()


answer = main({"firstStops": [747], "lastStops": [760], "timestamp": 1533644832})
print(answer)




# #######OLD#######
# def current_weather(request):
#
#     try:
#         first_row_of_table_as_dict = weather.objects.all().order_by("-timestamp")[:1].values()[0]
#         return JsonResponse(first_row_of_table_as_dict)
#     except:
#         client.captureException()
#
#
# def forecast(request):
#
#     try:
#         hour = dt.datetime.now().hour
#         day = dt.datetime.today().weekday()
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = %s AND hour = %s;", [day, hour])
#             row = cursor.fetchone()
#             dow = row[0]
#             hour = row[1]
#             temp = row[2]
#             rain = row[3]
#             forecast = {"dow": dow, "hour": hour, "temp": temp, "rain": rain}
#             return JsonResponse(forecast)
#     except:
#         client.captureException()
#
# def daily_forecast(request):
#     # The user will be able to select a date, which will translate into day below
#     try:
#         day = dt.datetime.today().weekday()
#         daily_forecast = []
#         for hour in range(24):
#             with connection.cursor() as cursor:
#                 cursor.execute(
#                     "SELECT dow, hour, temp, precip_intensity from DarkSky_hourly_weather_prediction WHERE dow = %s AND hour = %s;",
#                     [day, hour])
#                 row = cursor.fetchone()
#                 dow = row[0]
#                 hour = row[1]
#                 temp = row[2]
#                 rain = row[3]
#                 hourly_forecast = {"dow": dow, "hour": hour, "temp": temp, "rain": rain}
#                 daily_forecast.append(hourly_forecast)
#         all_day_weather = {"all_day_weather": daily_forecast}
#         return JsonResponse(all_day_weather)
#     except:
#         client.captureException()
#
#
# @csrf_exempt    # Can remove in production, needed for testing
# def make_prediction(request):
#     try:
#         # Convert JSON string passed by browser to Python dictionary:
#         values = json.loads(request.body.decode('utf-8'))
#
#         # # # # # # # # # # # # # # # # # # # # # # # #
#         # TODO: THIS IS FOR EVALUATION PURPOSES ONLY  #
#         # TODO: AND SHOULD BE REMOVED BEFORE RELEASE  #
#         # # # # # # # # # # # # # # # # # # # # # # # #
#
#         if values["username"]:
#             with open(f"{values['username'].lower()}_timer.txt", "w") as f:
#                 f.write(f"{segment}\n")
#                 f.write(f"{round(dt.datetime.timestamp(dt.datetime.now()))}\n")
#
#         prediction = {"result": segment, "message": f"Thank you {values['username']}; enjoy your trip!"}
#         return JsonResponse(prediction)
#     except:
#         client.captureException()
#
# @csrf_exempt
# def stop_location(request):
#
#     try:
#         values = json.loads(request.body.decode('utf-8'))
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT lat, `long` FROM static_bus_data WHERE stoppointid = %s LIMIT 1", [int(values["stop"])])
#             row = cursor.fetchone()
#             lat = row[0]
#             lng = row[1]
#
#         return JsonResponse({"lat": lat, "lng": lng})
#     except:
#         client.captureException()
#
#
# @csrf_exempt
# def stop_timer(request):
#
#     try:
#         username = json.loads(request.body.decode("utf-8"))["username"]
#
#         with open(f"{username.lower()}_timer.txt") as f:
#             x = f.readlines()
#
#         prediction = int(x[0])
#         actual = round((dt.datetime.timestamp(dt.datetime.now()) - int(x[1])) / 60)
#         percentage = round(((actual-prediction)/prediction) * 100, 2)
#
#         return JsonResponse({"prediction": prediction, "actual": actual, "percentage": percentage})
#     except:
#         client.captureException()
#
#
# @csrf_exempt
# def fare_finder(trip, stages):
#         # Do not use this function for any Xpress service and route 90
#         # Xpress services charge leap at 2.90 and cash at 3.65
#         # Route 90 charges leap at 1.50 and cash at 2.10
#     try:
#         leap = "€2.15"
#         cash = "€2.85"
#         stages = len(list(set(trip).intersection(stages)))
#         if stages < 4:
#             leap = "€1.50"
#             cash = "€2.10"
#         if stages > 12:
#             leap = "€2.60"
#             cash = "€3.30"
#         return([leap, cash])
#     except:
#         client.captureException()
#
#
#
#
#
