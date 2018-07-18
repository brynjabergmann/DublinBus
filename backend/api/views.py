from django.shortcuts import render
from django.http import JsonResponse


def current_weather(request):
    from api.models import DarkskyCurrentWeather as weather
    first_row_of_table_as_dict = weather.objects.all().order_by("-timestamp")[:1].values()[0]
    return JsonResponse(first_row_of_table_as_dict)
