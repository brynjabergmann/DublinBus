from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import json
import pickle
import pandas as pd
import datetime as dt
# from raven import Client

# IDEs might say this one is "unused", but once our models are unpickled they need sklearn:
import sklearn

# client = Client('https://1e979ddecb1641ce81a0468314902d26:e894e38ec1f64c43af6876f76a3d2959@sentry.io/1249736')


def predict(values: dict):
    first_stop_list = values["firstStops"]
    last_stop_list = values["lastStops"]
    user_time = values["timestamp"]

    weather = get_weather(user_time)

    all_routes = get_all_routes(first_stop_list, last_stop_list)
    all_journey_times = get_all_times(all_routes, weather, user_time)

    for i in range(len(all_routes)):    # Add the total time to the results sent to the user
        all_routes[i]["total_time"] = all_journey_times[i]

    result = {
        "routes": [
            # {
            #   "46A": {
            #       "stops": [768, 792],
            #       "fare": {
            #           "leap": 1.5,
            #           "cash": 2.1
            #       }
            #   ],
            #   "total_time": 20
            # }
        ],
        "delays": {
            "locations": [],
            "messages": []
        }
    }

    for i in range(3):
        fastest_route_index = get_fastest_route_index(all_journey_times)
        result["routes"].append(all_routes[fastest_route_index])
        del all_routes[fastest_route_index]
        del all_journey_times[fastest_route_index]

    midnight = user_time + 3600 - (user_time % 86400)   # TODO: This +3600 is DST
    five_am = midnight + (3600 * 5)
    eleven_pm = midnight + (3600 * 23)

    for route in result["routes"]:
        for hour in range(five_am, eleven_pm + 1, 3600):
            weather = get_weather(hour)
            route["hourly"].append(get_all_times([route], weather, hour))

    return result


def get_all_routes(first_stop_list: list, last_stop_list: list):
    paths = []
    for first_stop in first_stop_list:
        for last_stop in last_stop_list:
            for path in find_route(first_stop, last_stop):
                paths.append(path)
    return paths


def get_all_times(all_possible_routes: list, weather: dict, user_time: int):
    timings = []
    temperature = weather["temp"]
    precipitation = weather["precip_intensity"]

    for route in all_possible_routes:
        total_time = 0
        parts_of_route = [*route]
        for i in range(len(parts_of_route)):
            bus_route = parts_of_route[i]

            if "walk" in bus_route:
                total_time += route[i]
            else:
                direction = get_direction(bus_route, route[bus_route]["stops"][0])
                prediction = end_to_end_prediction(dt.datetime.fromtimestamp(user_time).weekday(),
                                                   dt.datetime.fromtimestamp(user_time - (user_time % 3600) + 3600).hour,  # TODO: This + 3600 is some DST fuckery that will ideally need to be dealt with.
                                                   temperature,
                                                   precipitation,
                                                   bus_route,
                                                   direction,
                                                   True)
                total_time += get_segment(prediction[0], bus_route, direction, route[bus_route]["stops"][0], route[bus_route]["stops"][1], prediction[1])
        timings.append(total_time)
    return timings


def get_fastest_route_index(all_times: list):
    best_route_index = 0
    fastest_time = 10000
    for index, value in enumerate(all_times):
        if value < fastest_time:
            best_route_index = index
            fastest_time = value

    return best_route_index


def get_segment(end_to_end: int, bus_route: str, direction: int, first_stop: int, last_stop: int, max_stops: int):
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
            row = cursor.fetchone()
        else:
            cursor.execute("SELECT temp, icon, precip_intensity FROM DarkSky_hourly_weather_prediction WHERE time = %s;", [utc_user_hour])
            row = cursor.fetchone()

    return {"temp": row[0], "icon": row[1], "precip_intensity": row[2]}


def end_to_end_prediction(day_of_week: int, hour_of_day: int, temperature: float, precipitation: float, bus_route: str, direction: int, school: bool):
    # Quick way to convert JS's day of week into a categorical feature:
    days_list = [0, 0, 0, 0, 0, 0, 0]
    days_list[day_of_week] = 1

    # Create a pandas dataframe to be fed into the prediction model
    prediction_inputs = pd.DataFrame({
        "avg_H": [hour_of_day],
        "DOW_Monday": [days_list[0]],
        "DOW_Tuesday": [days_list[1]],
        "DOW_Wednesday": [days_list[2]],
        "DOW_Thursday": [days_list[3]],
        "DOW_Friday": [days_list[4]],
        "DOW_Saturday": [days_list[5]],
        "DOW_Sunday": [days_list[6]],
        "temp": [temperature],
        "precip_intensity": [precipitation]
    })

    with open(f"api/models/GBR_school_2017_{bus_route}_{direction}.pkl", "rb") as f:
        cucumber = pickle.load(f)

    model = cucumber[0]
    max_stops = cucumber[1]
    prediction_minutes = int(round(model.predict(prediction_inputs)[0]))
    return [prediction_minutes, max_stops]  # Predict time from start to finish


def find_route(first_stop: int, last_stop: int):
    # TODO: This is unfinished. Right now it only works if the two stops provided share a route.
    with connection.cursor() as cursor:
        cursor.execute("SELECT one.line_id FROM (SELECT line_id FROM stops_served_by WHERE stop_number = %s) as one, (SELECT line_id FROM stops_served_by WHERE stop_number = %s) as two WHERE one.line_id = two.line_id;", [first_stop, last_stop])
        serves_both = list(cursor.fetchall())
        if serves_both:
            for line in serves_both[:]:
                cursor.execute("SELECT stop_on_route FROM combined_2017 WHERE line_id = %s AND stop_number = %s LIMIT 1;", [line, first_stop])
                progression_one = cursor.fetchone()[0]

                cursor.execute("SELECT stop_on_route FROM combined_2017 WHERE line_id = %s AND stop_number = %s LIMIT 1;", [line, last_stop])
                progression_two = cursor.fetchone()[0]

                if progression_one > progression_two:
                    serves_both.remove(line)

            return [
                {
                    x[0]: {
                        "stops": [first_stop, last_stop],
                        "fare": fare_finder(x[0], first_stop, last_stop)
                    }
                } for x in serves_both
            ]
        else:
            cursor.execute("SELECT line_id FROM stops_served_by WHERE stop_number = %s;", [first_stop])
            all_routes_first_stop = [x[0] for x in list(cursor.fetchall())]
            cursor.execute("SELECT line_id FROM stops_served_by WHERE stop_number = %s;", [last_stop])
            all_routes_last_stop = [x[0] for x in list(cursor.fetchall())]

            for route in all_routes_first_stop:
                cursor.execute()


def fare_finder(x, y, z):
    return {"leap": 2.15, "cash": 2.85}
# def fare_finder(route: str, direction: int, first_stop: int, last_stop: int):
#     if "x" in route.lower():
#         return {"leap": 2.90, "cash": 3.65}
#     elif route == "90":
#         return {"leap": 1.50, "cash": 2.10}
#     else:
#         # TODO: DB call to find number of stages
#         num_stages = 0
#         if num_stages < 4:
#             return {"leap": 1.50, "cash": 2.10}
#         elif num_stages > 12:
#             return {"leap": 2.60, "cash": 3.30}
#         else:
#             return {"leap": 2.15, "cash": 2.85}


def chart_values(route, timestamp):
    times = []
    midnight = timestamp - (timestamp % 86400)
    five_am = midnight + (3600 * 5)
    eleven_pm = midnight + (3600 * 23)
    for hour in range(five_am, eleven_pm + 1, 3600):
        # TODO: Have front-end communicate the above required values BACK to Django
        weather = get_weather(hour)
        times.append(get_all_times([route], weather, hour)[0])

    return times


# TODO: Re-implement this functionality for benchmarking
def start_timer(username: str, predicted_time: int):
    with open(f"{username.lower()}_timer.txt", "w") as f:
        f.write(f"{predicted_time}\n{dt.datetime.now().timestamp()}")


# TODO: This too
def stop_timer(username: str):
    with open(f"{username.lower()}_timer.txt") as f:
        x = f.readlines()

    prediction = int(x[0])
    actual = round((dt.datetime.timestamp(dt.datetime.now()) - int(x[1])) / 60)
    percentage = round(((actual - prediction) / prediction) * 100, 2)

    with open("accuracy_scores", "a") as g:
        g.write(f"Predicted: {prediction}, Actual: {actual} = {percentage}% error\n")

    return {"prediction": prediction, "actual": actual, "percentage": percentage}


# # # # # # # # # #
#  WEB ENDPOINTS  #
# # # # # # # # # #

@csrf_exempt
def prediction_endpoint(request):
    return JsonResponse(predict(json.loads(request.body.decode("utf-8"))))


@csrf_exempt
def current_weather_endpoint(request):
    return JsonResponse(get_weather(int(dt.datetime.now().timestamp())))


@csrf_exempt
def chart_endpoint(request):
    req = json.loads(request.body.decode("utf-8"))
    return JsonResponse(chart_values(req["route"], req["timestamp"]))
