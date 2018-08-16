from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import json
import pickle
import pandas as pd
import datetime as dt
import requests
# from raven import Client  # TODO: re-enable Raven for final push

# IDEs might say this one is "unused", but once our models are unpickled they need sklearn:
import sklearn

# client = Client('https://1e979ddecb1641ce81a0468314902d26:e894e38ec1f64c43af6876f76a3d2959@sentry.io/1249736')


def predict(first_stop_list: list, last_stop_list: list, user_time: int):
    weather = get_weather(user_time)

    all_itineraries = get_itineraries(first_stop_list, last_stop_list)
    all_journey_times = get_all_times(all_itineraries, weather, user_time)

    for i in range(len(all_itineraries)):  # Add the total time to the results sent to the user
        all_itineraries[i]["total_time"] = all_journey_times[i]

    result = {
        "itineraries": [
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

    for i in range(min(len(all_journey_times), 3)):
        fastest_journey_index = get_fastest_route_index(all_journey_times)
        result["itineraries"].append(all_itineraries[fastest_journey_index])
        del all_itineraries[fastest_journey_index]
        del all_journey_times[fastest_journey_index]

    return result


def get_itineraries(first_stop_list: list, last_stop_list: list):
    itineraries = []
    for first_stop in first_stop_list:
        for last_stop in last_stop_list:
            for itinerary in find_route(first_stop, last_stop):
                itineraries.append(itinerary)
    return itineraries


def get_all_times(all_possible_journeys: list, weather: dict, user_time: int):
    timings = []
    temperature = weather["temp"]
    precipitation = weather["precip_intensity"]

    for journey in all_possible_journeys:
        total_time = 0
        legs_of_journey = [*journey]
        for i in range(len(legs_of_journey)):
            bus_route = legs_of_journey[i]

            if "walk" in bus_route:
                total_time += journey["walk"]
            else:
                direction = get_direction(bus_route, journey[bus_route]["stops"][0])
                prediction = end_to_end_prediction(dt.datetime.fromtimestamp(user_time).weekday(),
                                                   dt.datetime.fromtimestamp(user_time - (user_time % 3600) + 3600).hour,
                                                   temperature,
                                                   precipitation,
                                                   bus_route,
                                                   direction,
                                                   is_school_holiday(user_time))
                total_time += get_segment(prediction[0], bus_route, direction, journey[bus_route]["stops"][0],
                                          journey[bus_route]["stops"][1], prediction[1])
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
    # TODO: Use calculated proportions.
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT stop_on_route FROM stops_served_by_two WHERE line_id = %s AND stop_number = %s AND direction = %s LIMIT 1;",
            [bus_route, first_stop, direction])
        stop_one = cursor.fetchone()[0]

        cursor.execute(
            "SELECT stop_on_route FROM stops_served_by_two WHERE line_id = %s AND stop_number = %s AND direction = %s LIMIT 1;",
            [bus_route, last_stop, direction])
        stop_two = cursor.fetchone()[0]

    return int(end_to_end * ((stop_two - stop_one) / max_stops))


def get_direction(bus_route: str, bus_stop: int):
    with connection.cursor() as cursor:
        cursor.execute("SELECT direction FROM stops_served_by_two WHERE line_id = %s AND stop_number = %s;",
                       [bus_route, bus_stop])
        return cursor.fetchone()[0]


def get_weather(timestamp: int):
    now = dt.datetime.now().timestamp()
    now_hour = now - (now % 3600)
    utc_user_hour = timestamp - (timestamp % 3600)

    if timestamp > dt.datetime.timestamp(dt.datetime.now() + dt.timedelta(days=7)):
        return {"temp": 10, "precip_intensity": 0}

    # No need for an Else, because this won't be reached if we return a value
    with connection.cursor() as cursor:
        if now_hour == utc_user_hour:
            cursor.execute(
                "SELECT temp, icon, precip_intensity FROM DarkSky_current_weather ORDER BY timestamp DESC LIMIT 1;")
            row = cursor.fetchone()
        else:
            cursor.execute(
                "SELECT temp, icon, precip_intensity FROM DarkSky_hourly_weather_prediction WHERE time = %s;",
                [utc_user_hour])
            row = cursor.fetchone()

    return {"temp": row[0], "icon": row[1], "precip_intensity": row[2]}


def end_to_end_prediction(day_of_week: int, hour_of_day: int, temperature: float, precipitation: float, bus_route: str,
                          direction: int, school_holiday: bool):
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

    if school_holiday:
        pickle_file = f"api/models/GBR_off_school_2017_{bus_route.upper()}_{direction}.pkl"
    else:
        pickle_file = f"api/models/GBR_school_2017_{bus_route.upper()}_{direction}.pkl"

    with open(pickle_file, "rb") as f:
        cucumber = pickle.load(f)

    model = cucumber[0]
    max_stops = cucumber[1]
    prediction_minutes = int(round(model.predict(prediction_inputs)[0]))
    return [prediction_minutes, max_stops]  # Predict time from start to finish


def find_route(first_stop: int, last_stop: int):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT one.line_id
                          FROM
                          (SELECT line_id FROM stops_served_by_two WHERE stop_number = %s) as one,
                          (SELECT line_id FROM stops_served_by WHERE stop_number = %s) as two
                          WHERE one.line_id = two.line_id;""",
                       [first_stop, last_stop])
        serves_both = list(cursor.fetchall())

        if serves_both:
            for line in serves_both[:]:
                cursor.execute(
                    "SELECT stop_on_route FROM stops_served_by_two WHERE line_id = %s AND stop_number = %s LIMIT 1;",
                    [line, first_stop])
                progression_one = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT stop_on_route FROM stops_served_by_two WHERE line_id = %s AND stop_number = %s LIMIT 1;",
                    [line, last_stop])
                progression_two = cursor.fetchone()[0]

                if progression_one > progression_two:
                    serves_both.remove(line)
            return [{x[0]: {
                "stops": [first_stop, last_stop],
                "fare": fare_finder(x[0], get_direction(x[0], first_stop), first_stop, last_stop)
            }
            } for x in serves_both]

        cursor.execute("SELECT line_id FROM stops_served_by_two WHERE stop_number = %s;", [first_stop])
        serves_first = [x[0] for x in cursor.fetchall()]

        cursor.execute("SELECT line_id FROM stops_served_by_two WHERE stop_number = %s;", [last_stop])
        serves_last = [x[0] for x in cursor.fetchall()]

        two_part_journeys = []
        for line in serves_first:
            same_direction = get_direction(line, first_stop)
            cursor.execute("SELECT stop_number FROM stops_served_by_two WHERE line_id = %s AND direction = %s",
                           [line, same_direction])
            for stop in [x[0] for x in cursor.fetchall()]:
                cursor.execute("SELECT line_id FROM stops_served_by_two WHERE stop_number = %s;", [stop])
                for connecting_line in [x[0] for x in cursor.fetchall()]:
                    if connecting_line in serves_last:
                        two_part_journeys.append(
                            {
                                line: {
                                    "stops": [first_stop, stop],
                                    "fare": fare_finder(line, same_direction, first_stop, stop)
                                },
                                connecting_line: {
                                    "stops": [stop, last_stop],
                                    "fare": fare_finder(connecting_line, get_direction(connecting_line, stop), stop,
                                                        last_stop)
                                }
                            }
                        )
        return two_part_journeys


def fare_finder(bus_route: str, direction: int, first_stop: int, last_stop: int):
    if "x" in bus_route.lower():
        return {"leap": 2.90, "cash": 3.65}
    elif bus_route == "90":
        return {"leap": 1.50, "cash": 2.10}
    else:
        with connection.cursor() as cursor:
            cursor.execute("""SELECT SUM(is_stage_marker)
                           FROM
                           (SELECT stop_on_route FROM stops_served_by_two WHERE line_id = %s AND direction = %s AND stop_number = %s) as first_stop,
                           (SELECT stop_on_route FROM stops_served_by_two WHERE line_id = %s AND direction = %s AND stop_number = %s) as second_stop,
                           (SELECT * FROM stops_served_by_two WHERE line_id = %s AND direction = %s) as all_stops
                           WHERE all_stops.stop_on_route >= first_stop.stop_on_route
                           AND all_stops.stop_on_route <= second_stop.stop_on_route;""",
                           [bus_route, direction, first_stop, bus_route, direction, last_stop, bus_route, direction])
            num_stages = cursor.fetchone()[0]

        if num_stages < 4:
            return {"leap": 1.50, "cash": 2.10}
        elif num_stages > 12:
            return {"leap": 2.60, "cash": 3.30}
        else:
            return {"leap": 2.15, "cash": 2.85}


def chart_values(itinerary: dict, timestamp: int):
    for bus_route in [*itinerary]:
        if bus_route != "walk":
            itinerary[bus_route]["stops"][0] = get_stopnum_from_location(itinerary[bus_route]["stops"][0][0], itinerary[bus_route]["stops"][0][1])
            itinerary[bus_route]["stops"][1] = get_stopnum_from_location(itinerary[bus_route]["stops"][1][0], itinerary[bus_route]["stops"][1][1])

    midnight = timestamp - (timestamp % 86400)
    five_am = midnight + (3600 * 5)
    eleven_pm = midnight + (3600 * 23)

    times = []
    for hour in range(five_am, eleven_pm + 1, 3600):
        weather = get_weather(hour)
        times.append(get_all_times([itinerary], weather, hour)[0])

    return times


def next_bus(stop_number: int, bus_route: str, direction: int, timestamp: int):
    # Note - This code works, but Dublin Bus's timetable endpoint is not consistently correct
    # Open https://data.smartdublin.ie/cgi-bin/rtpi/timetableinformation?type=week&stopid=2039&routeid=46A&format=json
    # and you will be able to see that as far as this system is concerned, the 46A stops running from Dun Laoghaire just
    # after midday Mon-Fri, which is not true no matter what timetable you're looking at.

    # with connection.cursor() as cursor:
    #     cursor.execute("SELECT stop_number FROM stops_served_by WHERE line_id = %s AND direction = %s AND stop_on_route = 1", [route, direction])
    #     first_stop = cursor.fetchone()
    user_dt = dt.datetime.fromtimestamp(timestamp)
    is_holiday = is_school_holiday(timestamp)
    year = user_dt.year
    month = user_dt.month
    date = user_dt.day
    day = user_dt.strftime("%A")

    timetable_json = requests.get(
        f"https://data.smartdublin.ie/cgi-bin/rtpi/timetableinformation?type=week&stopid={stop_number}&routeid={bus_route}&format=json").json()[
        "results"]

    if day == "Sunday":
        schedule = sorted(
            [list(dict.fromkeys(x["departures"])) for x in timetable_json if x["enddayofweek"] == "Sunday"],
            key=len, reverse=True)[:2]
    elif day == "Saturday":
        schedule = sorted(
            [list(dict.fromkeys(x["departures"])) for x in timetable_json if x["enddayofweek"] == "Saturday"], key=len,
            reverse=True)[:2]
    else:
        schedule = sorted(
            [list(dict.fromkeys(x["departures"])) for x in timetable_json if x["enddayofweek"] == "Friday"], key=len,
            reverse=True)[:2]

    if len(schedule) > 1 and dt.datetime.strptime(f"2018-01-01 {schedule[0][0]}",
                                                  "%Y-%m-%d %H:%M:%S") > dt.datetime.strptime(
            f"2018-01-01 {schedule[1][0]}", "%Y-%m-%d %H:%M:%S"):
        schedule = [int(dt.datetime.timestamp(dt.datetime.strptime(f"{year}-{month}-{date} {x}", "%Y-%m-%d %H:%M:%S")))
                    for x in schedule[1]]
    else:
        schedule = [int(dt.datetime.timestamp(dt.datetime.strptime(f"{year}-{month}-{date} {x}", "%Y-%m-%d %H:%M:%S")))
                    for x in schedule[0]]

    # TODO: Take every time from schedule, run a prediction from start to user's stop to generate all_arrival_times list
    all_arrival_times = []
    for time in schedule:
        schedule_dt = dt.datetime.fromtimestamp(time)
        weather = get_weather(time)
        e2e = end_to_end_prediction(schedule_dt.weekday(), schedule_dt.hour, weather["temp"],
                                    weather["precip_intensity"], bus_route, direction, is_holiday)
        all_arrival_times.append(
            schedule_dt + dt.timedelta(minutes=get_segment(e2e[0], bus_route, direction, 2039, stop_number, e2e[1])))

    next_buses = []
    for index, arrival_time in enumerate(all_arrival_times):
        if arrival_time > user_dt:
            for i in range(3):
                next_buses.append(all_arrival_times[index + i])
            break

    print()


def is_school_holiday(timestamp: int):
    year = dt.datetime.fromtimestamp(timestamp).year
    with open(f"api/school_holidays/{year}.json") as j:
        school_holidays = json.load(j)

    for holiday in school_holidays:
        if holiday[0] < timestamp < holiday[1]:
            return True

    return False


def get_stopnum_from_location(lat: float, lng: float):
    with connection.cursor() as cursor:
        cursor.execute("""SELECT stop_number
                          FROM static_bus_data
                          WHERE lat < %s + 0.0001 AND lat > %s - 0.0001
                          AND lng < %s + 0.0001 AND lng > %s - 0.0001""",
                       [lat, lat, lng, lng])
        row = cursor.fetchone()
        if row:
            return row[0]


def predict_from_locations(first_stop_lat: float, first_stop_lng: float, last_stop_lat: float, last_stop_lng: float, bus_route: str, timestamp: int):
    first_stop = get_stopnum_from_location(first_stop_lat, first_stop_lng)
    last_stop = get_stopnum_from_location(last_stop_lat, last_stop_lng)
    weather = get_weather(timestamp)
    user_dt = dt.datetime.fromtimestamp(timestamp)
    weekday = user_dt.weekday()
    hour = user_dt.hour
    temperature = weather["temp"]
    rain = weather["precip_intensity"]
    direction = get_direction(bus_route, first_stop)
    school_holiday = is_school_holiday(timestamp)

    e2e = end_to_end_prediction(weekday, hour, temperature, rain, bus_route, direction, school_holiday)
    return get_segment(e2e[0], bus_route, direction, first_stop, last_stop, e2e[1])


# TODO: Re-implement this functionality for benchmarking
def start_timer(username: str, predicted_time: int):
    with open(f"{username.lower()}_timer.txt", "w") as f:
        f.write(f"{predicted_time}\n{dt.datetime.now().timestamp()}")


# TODO: This too
def stop_timer(username: str):
    with open(f"{username.lower()}_timer.txt") as f:
        x = f.read().splitlines()

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
    req = json.loads(request.body.decode("utf-8"))
    return JsonResponse(predict(req["firstStops"], req["lastStops"], req["timestamp"]))


@csrf_exempt
def current_weather_endpoint(request):
    return JsonResponse(get_weather(int(dt.datetime.now().timestamp())))


@csrf_exempt
def chart_endpoint(request):
    req = json.loads(request.body.decode("utf-8"))
    return JsonResponse({"chart": chart_values(req["itinerary"], req["timestamp"])})


@csrf_exempt
def location_prediction_endpoint(request):
    req = json.loads(request.body.decode("utf-8"))
    predictions = []
    for request_dict in req:
        predictions.append(predict_from_locations(
            request_dict["firstStop"][0],
            request_dict["firstStop"][1],
            request_dict["lastStop"][0],
            request_dict["lastStop"][1],
            request_dict["busRoute"],
            request_dict["timestamp"]
        ))
    return JsonResponse(
        {
            "predictions": predictions
        }
    )
