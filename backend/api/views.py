from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import pickle
import pandas as pd
import os
import sklearn


def current_weather(request):
    from api.models import DarkskyCurrentWeather as weather
    first_row_of_table_as_dict = weather.objects.all().order_by("-timestamp")[:1].values()[0]
    return JsonResponse(first_row_of_table_as_dict)


@csrf_exempt    # Can remove in production, needed for testing
def make_prediction(request):
    values = json.loads(request.body.decode('utf-8'))

    days_list = [0, 0, 0, 0, 0, 0, 0]
    days_list[values["day"]] = 1

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

    with open(f"api/models/GBR_March_2017_{values['route']}_{values['direction']}.pkl", "rb") as f:
        model = pickle.load(f)

    end_to_end = int(round(model.predict(prediction_inputs)[0]))
    segment = int(end_to_end * (values["num_stops"] / values["max_stops"]))
    prediction = {"result": segment}

    return JsonResponse(prediction)
