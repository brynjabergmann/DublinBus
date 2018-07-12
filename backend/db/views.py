from django.shortcuts import render
from django.http import JsonResponse


def current_weather(request):
    from db.models import DarkskyCurrentWeather as weather
    
    # modelName.objects.all() gets a QuerySet of all rows in the table (aka model)
    # [:1] says we actually only want the first row
    # .values() converts from a QuerySet to a list of dicts (one dict per row)
    # [0] gets the first dict in the list (in this case we only have one
    first_row_of_table_as_dict = weather.objects.all().order_by("-timestamp")[:1].values()[0]

    # This automatically serialises the above to JSON and sends it as a HTTP response.
    return JsonResponse(first_row_of_table_as_dict)
